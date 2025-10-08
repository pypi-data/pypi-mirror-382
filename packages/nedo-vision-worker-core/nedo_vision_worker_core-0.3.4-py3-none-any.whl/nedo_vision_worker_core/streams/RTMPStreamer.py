import subprocess
import logging
import threading
import time
import numpy as np
import os
import sys
import cv2
import queue
from typing import Optional
from ..util.PlatformDetector import PlatformDetector

class RTMPStreamer:
    """
    Streams raw BGR frames to an RTMP server using a GStreamer-first approach
    with a reliable FFmpeg subprocess fallback.
    """

    def __init__(self, pipeline_id: str, fps: int = 25, bitrate: str = "1500k"):
        self.rtmp_server = os.environ.get("RTMP_SERVER", "rtmp://localhost:1935/live")
        self.rtmp_url = f"{self.rtmp_server}/{pipeline_id}"
        self.fps = max(int(fps), 1)
        self.bitrate = self._kbps(bitrate) # Store as integer kbps

        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self._platform = PlatformDetector()
        
        self._backend = None # "gstreamer" or "ffmpeg"
        self._gstreamer_writer: Optional[cv2.VideoWriter] = None
        self._ffmpeg_process: Optional[subprocess.Popen] = None

        self._frame_queue = queue.Queue(maxsize=2)
        self._writer_thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()

    def _kbps(self, rate_str: str) -> int:
        return int(str(rate_str).lower().replace("k", "").strip())

    # -------------------- Public API --------------------

    def is_active(self) -> bool:
        if self._backend == "gstreamer":
            return self._gstreamer_writer is not None and self._gstreamer_writer.isOpened()
        if self._backend == "ffmpeg":
            return self._ffmpeg_process is not None and self._ffmpeg_process.poll() is None
        return False

    def push_frame(self, frame: np.ndarray):
        if self._stop_evt.is_set():
            return

        if self._writer_thread is None or not self._writer_thread.is_alive():
            if frame is None: return
            self.height, self.width = frame.shape[:2]
            self._start_stream()

        try:
            self._frame_queue.put_nowait(frame)
        except queue.Full:
            try:
                self._frame_queue.get_nowait()
                self._frame_queue.put_nowait(frame)
            except queue.Empty:
                pass

    def stop_stream(self):
        if self._stop_evt.is_set():
            return
        logging.info(f"Stopping RTMP stream for {self.rtmp_url}")
        self._stop_evt.set()
        
        try:
            self._frame_queue.put_nowait(None)
        except queue.Full:
            pass

        if self._writer_thread and self._writer_thread.is_alive() and threading.current_thread() != self._writer_thread:
            self._writer_thread.join(timeout=2.0)

        if self._gstreamer_writer:
            self._gstreamer_writer.release()
            self._gstreamer_writer = None
            logging.info("GStreamer writer released.")
        
        if self._ffmpeg_process:
            try:
                if self._ffmpeg_process.stdin: self._ffmpeg_process.stdin.close()
                self._ffmpeg_process.terminate()
                self._ffmpeg_process.wait(timeout=2.0)
            except Exception:
                if self._ffmpeg_process: self._ffmpeg_process.kill()
            self._ffmpeg_process = None
            logging.info("FFmpeg process stopped.")
        
        self._backend = None

    # -------------------- Internal Stream Management --------------------

    def _start_stream(self):
        self._stop_evt.clear()
        
        gstreamer_pipeline = self._build_gstreamer_pipeline()
        self._gstreamer_writer = cv2.VideoWriter(gstreamer_pipeline, cv2.CAP_GSTREAMER, 0, self.fps, (self.width, self.height))

        if self._gstreamer_writer.isOpened():
            self._backend = "gstreamer"
            self._writer_thread = threading.Thread(target=self._gstreamer_writer_loop, daemon=True)
            self._writer_thread.start()
            logging.info(f"RTMP streaming started with GStreamer (HW-Accel): {self.rtmp_url}")
            return
        
        logging.warning("GStreamer VideoWriter failed to open. Falling back to FFmpeg subprocess.")
        self._gstreamer_writer = None

        cmd = self._build_ffmpeg_cmd()
        try:
            self._ffmpeg_process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._backend = "ffmpeg"
            self._writer_thread = threading.Thread(target=self._ffmpeg_pacing_loop, daemon=True)
            self._writer_thread.start()
            logging.info(f"RTMP streaming started with FFmpeg (Fallback): {self.rtmp_url}")
        except Exception as e:
            logging.error(f"Failed to start FFmpeg fallback: {e}")
            self._ffmpeg_process = None

    def _gstreamer_writer_loop(self):
        while not self._stop_evt.is_set():
            try:
                frame = self._frame_queue.get(timeout=1.0)
                if frame is None:
                    break
                self._gstreamer_writer.write(frame)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error in GStreamer writer loop: {e}. Stopping thread.")
                self._stop_evt.set()
                break

    # -------------------- Pipeline Builders --------------------

    def _build_gstreamer_pipeline(self) -> str:
        if self._platform.is_jetson():
            encoder = "nvv4l2h264enc insert-sps-pps=true"
            converter = "nvvidconv ! video/x-raw(memory:NVMM) ! "
        else:
            encoder = "nvh264enc preset=low-latency-hq"
            converter = "videoconvert"

        pipeline = (
            f"appsrc ! "
            f"video/x-raw,format=BGR,width={self.width},height={self.height},framerate={self.fps}/1 ! "
            f"{converter} ! {encoder} bitrate={self.bitrate} ! "
            f"h264parse ! flvmux ! "
            f"rtmpsink location=\"{self.rtmp_url}\""
        )
        return pipeline

    # --- FFmpeg Fallback Methods ---
    
    def _ffmpeg_pacing_loop(self):
        frame_period = 1.0 / self.fps
        last_frame_sent = None

        while not self._stop_evt.is_set():
            start_time = time.monotonic()
            
            try:
                frame = self._frame_queue.get_nowait()
                last_frame_sent = frame
            except queue.Empty:
                frame = last_frame_sent

            if frame is None:
                time.sleep(frame_period)
                continue

            try:
                if not self.is_active():
                    raise BrokenPipeError("FFmpeg process is not active")
                self._ffmpeg_process.stdin.write(frame.tobytes())
            except (BrokenPipeError, OSError) as e:
                logging.error(f"FFmpeg process pipe broken: {e}. Stopping thread.")
                self._stop_evt.set()
                break
            
            elapsed = time.monotonic() - start_time
            sleep_duration = max(0, frame_period - elapsed)
            time.sleep(sleep_duration)

    def _build_ffmpeg_cmd(self) -> list[str]:
        encoder_args = self._select_ffmpeg_encoder()
        encoder_name = encoder_args[1]

        # Base command arguments
        cmd = [
            'ffmpeg', '-y', '-loglevel', 'error', '-nostats', '-hide_banner',
            '-f', 'rawvideo', '-pixel_format', 'bgr24',
            '-video_size', f'{self.width}x{self.height}',
            '-framerate', str(self.fps), '-i', '-',
        ]

        # Add the selected encoder
        cmd.extend(encoder_args)

        # Add common arguments for all encoders
        cmd.extend([
            '-profile:v', 'main', '-pix_fmt', 'yuv420p',
            '-b:v', f"{self.bitrate}k", '-maxrate', f"{self.bitrate}k", '-bufsize', f"{self.bitrate*2}k",
            '-g', str(self.fps), '-keyint_min', str(self.fps),
            '-force_key_frames', 'expr:gte(t,n_forced*1)', '-an',
            '-flvflags', 'no_duration_filesize', '-f', 'flv', self.rtmp_url,
        ])
        
        # Conditionally add arguments that are ONLY valid for the libx264 encoder
        if encoder_name == "libx264":
            cmd.extend([
                "-tune", "zerolatency",
                "-x264-params", "open_gop=0:aud=1:repeat-headers=1:nal-hrd=cbr",
            ])
        
        return cmd

    def _select_ffmpeg_encoder(self) -> list:
        if sys.platform == "darwin": return ["-c:v", "h264_videotoolbox"]
        if os.environ.get("NVIDIA_VISIBLE_DEVICES") is not None or os.path.exists("/proc/driver/nvidia/version"):
            return ["-c:v", "h264_nvenc", "-preset", "llhp"]
        return ["-c:v", "libx264"]