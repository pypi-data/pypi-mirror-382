import os
import cv2
import time
import threading
import logging
from typing import Optional, Union, List, Dict
from enum import Enum
from ..util.PlatformDetector import PlatformDetector

import numpy as np
from numpy.typing import NDArray
MatLike = NDArray[np.uint8]

# ---------- States and Enums ----------
class StreamState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    STOPPED = "stopped"

class HWAccel(Enum):
    """Hardware acceleration preference."""
    AUTO = "auto"
    NVDEC = "nvdec"
    NONE = "none"

# ---------- FFmpeg / RTSP tuning (for fallback) ----------
def set_ffmpeg_rtsp_env(
    *,
    prefer_tcp: bool = True,
    probesize: str = "256k",
    analyzeduration_us: int = 1_000_000,
    buffer_size: str = "256k",
    max_delay_us: int = 700_000,
    stimeout_us: int = 5_000_000
) -> None:
    """Sets environment variables for OpenCV's FFmpeg backend."""
    opts = [
        f"rtsp_transport;{'tcp' if prefer_tcp else 'udp'}",
        f"probesize;{probesize}",
        f"analyzeduration;{analyzeduration_us}",
        f"buffer_size;{buffer_size}",
        f"max_delay;{max_delay_us}",
        f"stimeout;{stimeout_us}",
        "flags;low_delay",
        "rtsp_flags;prefer_tcp" if prefer_tcp else "",
    ]
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "|".join([o for o in opts if o])

# ---------- VideoStream with NVDEC support ----------
class VideoStream(threading.Thread):
    """
    RTSP/file capture that prioritizes low-latency hardware decoding (NVDEC)
    with a robust fallback to CPU-based decoding.
    """

    def __init__(
        self,
        source: Union[str, int],
        *,
        hw_accel: HWAccel = HWAccel.AUTO,
        video_codec: str = "h264",
        reconnect_interval: float = 5.0,
        max_failures: int = 5,
        max_reconnect_attempts: int = 10,
        backoff_factor: float = 1.5,
        max_sleep_backoff: float = 60.0,
        target_fps: Optional[float] = None,
        enable_backlog_drain: bool = False,
        ffmpeg_prefer_tcp: bool = True
    ):
        super().__init__(daemon=True)

        self.source = source
        self.reconnect_interval = reconnect_interval
        self.max_failures = max_failures
        self.max_reconnect_attempts = max_reconnect_attempts
        self.backoff_factor = backoff_factor
        self.max_sleep_backoff = max_sleep_backoff
        self.target_fps = target_fps
        self._drain_backlog = enable_backlog_drain
        self.ffmpeg_prefer_tcp = ffmpeg_prefer_tcp

        self.hw_accel = hw_accel
        self.video_codec = video_codec.lower()
        self._platform = PlatformDetector()
        self._current_backend: Optional[str] = None

        self.capture: Optional[cv2.VideoCapture] = None
        self.state: StreamState = StreamState.DISCONNECTED
        self.fps: float = 30.0
        self.frame_count: int = 0
        self.start_time: float = time.time()
        self.running: bool = True

        self._first_frame_evt = threading.Event()

        self._latest_frame_lock = threading.Lock()
        self._latest_frame: Optional[MatLike] = None

        self._buffer_lock = threading.Lock()
        self._buf_a: Optional[MatLike] = None
        self._buf_b: Optional[MatLike] = None
        self._active_buf: str = "a"

        self._reconnect_attempts = 0
        self._current_interval = reconnect_interval

        self._codec_info: Optional[str] = None
        self._last_frame_ts: float = 0.0
        self.is_file = self._is_file_source()

    def _is_file_source(self) -> bool:
        source_str = str(self.source)
        if source_str.startswith(("rtsp://", "rtmp://", "http://", "https://")):
            return False
        if isinstance(self.source, int):
            return False
        return os.path.isfile(source_str)

    def _get_source_for_cv2(self) -> Union[str, int]:
        if isinstance(self.source, str) and self.source.isdigit():
            return int(self.source)
        return self.source

    def _build_nvv4l2_pipeline(self) -> Optional[str]:
        """Hardware decode pipeline for NVIDIA Jetson devices."""
        if self.video_codec == 'h264':
            depay_parse = "rtpjitterbuffer ! rtph264depay ! h264parse"
        elif self.video_codec == 'h265':
            depay_parse = "rtpjitterbuffer ! rtph265depay ! h265parse"
        else:
            return None

        pipeline = (
            f"rtspsrc location=\"{self.source}\" latency=200 protocols=tcp ! "
            f"{depay_parse} ! nvv4l2decoder ! "
            "nvvidconv ! video/x-raw, format=BGRx ! "
            "videoconvert ! video/x-raw, format=BGR ! "
            "appsink drop=1 max-buffers=1"
        )
        return pipeline
        
    def _build_nvcodec_pipeline(self) -> Optional[str]:
        """Hardware decode pipeline for Linux systems with NVIDIA dGPUs."""
        if self.video_codec == 'h264':
            decoder_element = "nvh264dec"
            depay_parse = "rtpjitterbuffer ! rtph264depay ! h264parse config-interval=-1"
        elif self.video_codec == 'h265':
            decoder_element = "nvh265dec"
            depay_parse = "rtpjitterbuffer ! rtph265depay ! h265parse config-interval=-1"
        else:
            return None

        pipeline = (
            f"rtspsrc location=\"{self.source}\" latency=200 protocols=tcp ! "
            f"{depay_parse} ! {decoder_element} ! "
            "videoconvert ! video/x-raw,format=BGR ! "
            "appsink max-buffers=1 drop=true sync=false"
        )
        return pipeline

    def _initialize_capture(self) -> bool:
        self.state = StreamState.CONNECTING
        logging.info(f"Connecting to {self.source} (attempt {self._reconnect_attempts + 1})")
        if self.capture:
            self.capture.release()

        is_supported = self._platform.is_linux() and self._platform.has_gstreamer() and self._platform.has_nvidia_gpu()
        use_nvdec = (self.hw_accel != HWAccel.NONE) and is_supported

        # For RTSP streams, try GStreamer with hardware acceleration first
        if not self.is_file and use_nvdec:
            # Choose the best pipeline based on the platform
            if self._platform.is_jetson():
                logging.info("Jetson platform detected. Prioritizing nvv4l2decoder.")
                pipeline = self._build_nvv4l2_pipeline()
                backend_name = "gstreamer_nvv4l2"
            else:
                logging.info("dGPU platform detected. Prioritizing nvcodec.")
                pipeline = self._build_nvcodec_pipeline()
                backend_name = "gstreamer_nvcodec"

            if pipeline:
                self.capture = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
                if self.capture.isOpened():
                    self._current_backend = backend_name

        # Fallback for local files, or if GStreamer failed
        if not self.capture or not self.capture.isOpened():
            if not self.is_file and use_nvdec:
                logging.warning("Primary GStreamer pipeline failed. Falling back to FFmpeg/CPU.")
            elif self.is_file:
                 logging.info("Source is a file. Using FFmpeg backend.")

            if not self.is_file:
                 set_ffmpeg_rtsp_env(prefer_tcp=self.ffmpeg_prefer_tcp)

            self.capture = cv2.VideoCapture(self._get_source_for_cv2(), cv2.CAP_FFMPEG)
            if self.capture.isOpened():
                self._current_backend = "ffmpeg_cpu" if not self.is_file else "ffmpeg_file"

        if not self.capture or not self.capture.isOpened():
            logging.error(f"Failed to open video source: {self.source}")
            return False

        logging.info(f"Successfully opened stream using '{self._current_backend}' backend.")
        self._configure_capture()
        self.state = StreamState.CONNECTED
        return True

    def _configure_capture(self) -> None:
        is_gstreamer = self._current_backend and "gstreamer" in self._current_backend

        if not is_gstreamer:
            try:
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
                
            try:
                fourcc = int(self.capture.get(cv2.CAP_PROP_FOURCC))
                if fourcc:
                    self._codec_info = "".join([chr((fourcc >> (8 * i)) & 0xFF) for i in range(4)])
            except Exception:
                pass

        detected_fps = self.capture.get(cv2.CAP_PROP_FPS)
        if detected_fps and 0 < detected_fps <= 240:
            self.fps = detected_fps
        else:
            self.fps = 30.0
        
        logging.info(f"Stream connected at ~{self.fps:.1f} FPS. Codec: {self._codec_info or 'N/A'}")

    def run(self) -> None:
        """Main capture loop."""
        failures = 0
        while self.running:
            try:
                if not self.capture or not self.capture.isOpened():
                    if not self._initialize_capture():
                        if not self._handle_reconnection():
                            break
                        continue
                    failures = 0
                    self._reconnect_attempts = 0
                    self._current_interval = self.reconnect_interval

                ret, frame = self.capture.read()

                if not ret or frame is None:
                    if self._handle_file_end():
                        continue
                    
                    failures += 1
                    if failures > self.max_failures:
                        logging.error("Too many consecutive read failures; forcing reconnect.")
                        self._cleanup_capture()
                        failures = 0
                    time.sleep(0.02)
                    continue

                failures = 0
                self.frame_count += 1
                self._publish_latest(frame)

            except Exception as e:
                logging.error(f"Unexpected error in capture loop: {e}", exc_info=True)
                self._cleanup_capture()
                if not self._sleep_interruptible(self.reconnect_interval):
                    break
        
        self._final_cleanup()

    def stop(self, timeout: float = 5.0) -> None:
        if not self.running:
            return
        logging.info(f"Stopping VideoStream: {self.source}")
        self.running = False
        if self.is_alive():
            self.join(timeout=timeout)

    def _cleanup_capture(self) -> None:
        if self.capture:
            try:
                self.capture.release()
            except Exception as e:
                logging.error(f"Error releasing capture: {e}")
            finally:
                self.capture = None
        self.state = StreamState.DISCONNECTED

    def _sleep_interruptible(self, duration: float) -> bool:
        end = time.perf_counter() + duration
        while self.running and time.perf_counter() < end:
            time.sleep(0.05)
        return self.running



    def _handle_reconnection(self) -> bool:
        if self.is_file or self._reconnect_attempts >= self.max_reconnect_attempts:
            return False
        
        self._reconnect_attempts += 1
        self.state = StreamState.RECONNECTING
        self._current_interval = min(self._current_interval * self.backoff_factor, self.max_sleep_backoff)
        logging.warning(f"Reconnecting in {self._current_interval:.1f}s...")
        return self._sleep_interruptible(self._current_interval)

    def _handle_file_end(self) -> bool:
        if not self.is_file:
            return False
        
        current_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)

        if total_frames > 0 and current_frame >= total_frames:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return True
        
        return False

    def _publish_latest(self, frame: MatLike) -> None:
        with self._buffer_lock:
            if self._active_buf == "a":
                self._buf_b = frame
                self._active_buf = "b"
            else:
                self._buf_a = frame
                self._active_buf = "a"
        
        with self._latest_frame_lock:
            src = self._buf_b if self._active_buf == "b" else self._buf_a
            self._latest_frame = None if src is None else src.copy()
            if not self._first_frame_evt.is_set() and self._latest_frame is not None:
                self._first_frame_evt.set()
        
        self._last_frame_ts = time.perf_counter()

    def get_frame(self) -> Optional[MatLike]:
        if not self.running or self.state != StreamState.CONNECTED:
            return None
        with self._latest_frame_lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def wait_first_frame(self, timeout: float = 10.0) -> bool:
        return self._first_frame_evt.wait(timeout)

    def is_connected(self) -> bool:
        return self.state == StreamState.CONNECTED
    
    def get_state(self) -> StreamState:
        return self.state
        
    def _final_cleanup(self) -> None:
        self.state = StreamState.STOPPED
        self._cleanup_capture()
        logging.info(f"VideoStream stopped: {self.source}")