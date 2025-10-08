import logging
import time
import threading
import queue
from ..detection.detection_processing.HumanDetectionProcessor import HumanDetectionProcessor
from ..detection.detection_processing.PPEDetectionProcessor import PPEDetectionProcessor
from .PipelineConfigManager import PipelineConfigManager
from .PipelinePrepocessor import PipelinePrepocessor
from ..repositories.WorkerSourcePipelineDebugRepository import WorkerSourcePipelineDebugRepository
from ..repositories.WorkerSourcePipelineDetectionRepository import WorkerSourcePipelineDetectionRepository
from ..streams.VideoStreamManager import VideoStreamManager
from ..ai.VideoDebugger import VideoDebugger
from ..ai.FrameDrawer import FrameDrawer
from ..tracker.TrackerManager import TrackerManager
from ..detection.BaseDetector import BaseDetector
from ..streams.RTMPStreamer import RTMPStreamer


class PipelineProcessor:
    """Handles pipeline processing including preprocessing, AI model inference, tracking, and video stream processing."""

    def __init__(self, pipeline, detector: BaseDetector, enable_visualization=True):
        self._pipeline = pipeline
        self.running = True
        self.video_debugger = VideoDebugger(enable_visualization)
        self.tracker_manager = TrackerManager()
        self.detector = detector
        self.config_manager = PipelineConfigManager()
        self.preprocessor = PipelinePrepocessor()
        self.detection_processor = None
        self.threshold = 0.7

        # Keep the latest frame for detection; size=1 and we overwrite when full
        self.frame_queue = queue.Queue(maxsize=1)

        self.tracked_objects_render = []
        self.detection_thread = None
        self.frame_counter = 0
        self.frame_drawer = FrameDrawer()
        self.pipeline_id = pipeline.id
        self.worker_source_id = pipeline.worker_source_id

        self.rtmp_streamer = None

        self.detection_processor_codes = [
            PPEDetectionProcessor.code,
            HumanDetectionProcessor.code,
        ]

        self.debug_flag = False
        self.debug_repo = WorkerSourcePipelineDebugRepository()
        self.detection_repo = WorkerSourcePipelineDetectionRepository()
        
        # Frame recovery mechanism
        self.consecutive_frame_failures = 0
        self.max_consecutive_failures = 150  # 1.5 seconds at 0.01s intervals
        self.last_successful_frame_time = time.time()
        self.stream_recovery_timeout = 30.0  # 30 seconds timeout for stream recovery
        
        # HEVC error tracking
        self.hevc_error_count = 0
        self.last_hevc_recovery = 0
        self.hevc_recovery_cooldown = 30.0  # 30 seconds between HEVC recovery attempts

    def update_config(self, pipeline):
        """Updates the pipeline configuration."""
        self._pipeline = pipeline
        self._update_config_internal()

    def load_detector(self, detector: BaseDetector):
        logging.info(f"🔄 Loading new detector for pipeline {self.pipeline_id}")
        self.detector = detector
        self._update_detection_processor()
        logging.info(f"✅ Detector updated for pipeline {self.pipeline_id}")

    def _get_detection_processor_code(self):
        for code in self.detection_processor_codes:
            if self.config_manager.is_feature_enabled(code):
                return code
        return None
    
    def _get_detection_processor(self, code):
        if code == PPEDetectionProcessor.code:
            return PPEDetectionProcessor()
        elif code == HumanDetectionProcessor.code:
            return HumanDetectionProcessor()
        else:
            return None
    
    def _update_detection_processor(self):
        code = self._get_detection_processor_code()
        if self.detection_processor and self.detection_processor.code == code:
            return
        
        self.detection_processor = self._get_detection_processor(code)
        if self.detection_processor:
            self.frame_drawer.update_config(
                icons=self.detection_processor.icons,
                violation_labels=self.detection_processor.violation_labels,
                compliance_labels=self.detection_processor.compliance_labels,
            )
            multi_instance_classes = []
            if hasattr(self.detection_processor, 'get_multi_instance_classes'):
                multi_instance_classes = self.detection_processor.get_multi_instance_classes()
            
            self.tracker_manager.update_config(
                attribute_labels=self.detection_processor.labels,
                exclusive_attribute_groups=self.detection_processor.exclusive_labels,
                multi_instance_classes=multi_instance_classes
            )
        else:
            # Reset drawer/tracker when no processor enabled
            self.frame_drawer.update_config()
            self.tracker_manager.update_config([], [], [])

    def _update_config_internal(self):
        self.config_manager.update(self.pipeline_id)
        self.preprocessor.update(self.config_manager)
        self.detection_interval = self._get_detection_interval()
        self._update_detection_processor()
        
        # Reset failure counters on config update
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()

        ai_model = self.detector.metadata if self.detector else None
        if self.detection_processor:
            config = self.config_manager.get_feature_config(self.detection_processor.code)
            self.detection_processor.update(self.config_manager, ai_model)
            self.threshold = config.get("minimumDetectionConfidence", 0.7)

            if self.detection_processor.code == HumanDetectionProcessor.code:
                self.frame_drawer.polygons = [((0, 0, 255), p) for p in self.detection_processor.restricted_areas]
        else:
            self.threshold = 0.7

    def process_pipeline(self, video_manager: VideoStreamManager):
        pipeline_id = self.pipeline_id
        worker_source_id = self.worker_source_id
        logging.info(f"🎯 Running pipeline processing for pipeline {pipeline_id} | Source: {worker_source_id}")

        self._update_config_internal()
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()

        initial_frame = self._wait_for_frame(video_manager)
        if initial_frame is None:
            logging.error(f"❌ Pipeline {pipeline_id} | Source {worker_source_id}: No initial frame available. Exiting...")
            return

        # Start RTMP (internal pacer thread will begin on first push_frame())
        self.rtmp_streamer = RTMPStreamer(pipeline_id)

        # Start detection thread
        self.detection_thread = threading.Thread(
            target=self._detection_worker,
            name=f"detection-{pipeline_id}",
            daemon=True
        )
        self.detection_thread.start()

        try:
            while self.running:
                frame = video_manager.get_frame(worker_source_id)

                if frame is None:
                    if not self._handle_frame_failure(video_manager, worker_source_id):
                        break
                    # no frame this tick—just continue (the streamer will repeat last good frame)
                    continue
                    
                # cv2.imshow("AA", frame)
                # cv2.waitKey(1)
                # continue
                
                # successful frame
                self.consecutive_frame_failures = 0
                self.last_successful_frame_time = time.time()
                self.frame_counter += 1

                # draw annotations
                try:
                    self.frame_drawer.draw_polygons(frame)
                    drawn_frame = self.frame_drawer.draw_frame(
                        frame.copy(),
                        self.tracked_objects_render,
                        with_trails=True,
                        trail_length=int(max(1, 2 / self.detection_interval))
                    )
                except Exception as e:
                    logging.error(f"❌ Draw failed, using raw frame: {e}")
                    drawn_frame = frame

                # debug snapshot if requested
                if self.debug_flag:
                    tracked_objects_render = self._process_frame(frame)
                    try:
                        self.debug_repo.update_debug_entries_by_pipeline_id(
                            self.pipeline_id,
                            self.frame_drawer.draw_frame(frame.copy(), tracked_objects_render),
                            tracked_objects_render
                        )
                    except Exception as e:
                        logging.warning(f"Debug save failed: {e}")
                    self.debug_flag = False

                # ---- RTMP push (latest-only; pacing handled inside RTMPStreamer) ----
                if self.rtmp_streamer is None or not self.rtmp_streamer.is_active():
                    # (re)create; it will learn WxH on first push
                    self.rtmp_streamer = RTMPStreamer(self.pipeline_id)

                try:
                    self.rtmp_streamer.push_frame(drawn_frame)
                except Exception as e:
                    logging.error(f"❌ RTMP push error: {e}")
                    try:
                        self.rtmp_streamer.stop_stream()
                    except Exception:
                        pass
                    self.rtmp_streamer = None

                # feed detection worker with latest-only behavior
                if self.detection_thread and self.detection_thread.is_alive():
                    try:
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        try:
                            _ = self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                        try:
                            self.frame_queue.put_nowait(frame)
                        except queue.Full:
                            pass

                # visualize
                try:
                    self.video_debugger.show_frame(pipeline_id, worker_source_id, drawn_frame)
                except Exception as e:
                    logging.error(f"⚠️ Failed to render frame for pipeline {pipeline_id}: {e}")
                
                time.sleep(0.1)

        except Exception as e:
            logging.error(f"❌ Error in pipeline {pipeline_id}: {e}", exc_info=True)

    def _process_frame(self, frame):
        dimension = frame.shape[:2]
        processed_frame = self.preprocessor.apply(frame)
        
        class_thresholds = {}
        ai_model = self.detector.metadata if self.detector else None
        
        if self.detection_processor:
            if self.detection_processor.code == PPEDetectionProcessor.code:
                class_thresholds.update(self.detection_processor.get_class_thresholds())
            elif self.detection_processor.code == HumanDetectionProcessor.code:
                main_threshold = self.detection_processor.get_main_class_threshold(ai_model)
                if main_threshold and ai_model and ai_model.get_main_class():
                    class_thresholds[ai_model.get_main_class()] = main_threshold
        
        detections = []
        if self.detector:
            detections = self.detector.detect_objects(processed_frame, self.threshold, class_thresholds)
        
        detections = self.preprocessor.revert_detections_bboxes(detections, dimension)
        
        if self.detection_processor:
            matched_results = self.detection_processor.process(detections, dimension)
            return self.tracker_manager.track_objects(matched_results)
        else:
            return self.tracker_manager.track_objects(detections)

    def _detection_worker(self):
        """Runs detection in a separate thread and updates configuration periodically."""
        pipeline_id = self.pipeline_id
        worker_source_id = self.worker_source_id
        last_detection_time = time.time()
        last_config_update_time = time.time()
        config_update_interval = 5  # seconds

        while self.running:
            try:
                frame = self.frame_queue.get(block=True, timeout=1)
                current_time = time.time()

                # Update config periodically
                if (current_time - last_config_update_time) >= config_update_interval:
                    self._update_config_internal()
                    last_config_update_time = current_time

                # Keep only the latest frame if we fell behind
                try:
                    while True:
                        newer = self.frame_queue.get_nowait()
                        frame = newer
                except queue.Empty:
                    pass

                # Respect detection interval
                if (current_time - last_detection_time) < self.detection_interval:
                    continue
                last_detection_time = current_time

                if self.detection_processor is None or frame is None or frame.size == 0:
                    self.tracked_objects_render = []
                    continue

                self.tracked_objects_render = self._process_frame(frame)
                
                # Save to database if enabled
                if self.config_manager.is_feature_enabled("db"):
                    self.detection_processor.save_to_db(
                        pipeline_id,
                        worker_source_id,
                        self.frame_counter,
                        self.tracked_objects_render,
                        frame,
                        self.frame_drawer
                    )

                if self.config_manager.is_feature_enabled("webhook") or self.config_manager.is_feature_enabled("mqtt"):
                    self.detection_repo.save_detection(
                        pipeline_id,
                        frame,
                        self.tracked_objects_render,
                        self.frame_drawer
                    )

            except queue.Empty:
                pass
            except Exception as e:
                logging.error(f"❌ Error in detection thread for pipeline {pipeline_id}: {e}", exc_info=True)
    
    def _wait_for_frame(self, video_manager, max_wait_time=30.0):
        logging.info(f"⏳ Waiting for initial frame from {self.worker_source_id}...")
        
        is_ready = video_manager.wait_for_stream_ready(self.worker_source_id, timeout=max_wait_time)

        if is_ready:
            frame = video_manager.get_frame(self.worker_source_id)
            if frame is not None:
                logging.info(f"✅ Initial frame received from {self.worker_source_id}")
                return frame
            else:
                logging.error(f"❌ Stream {self.worker_source_id} reported ready, but the first frame could not be retrieved.")
                self._log_stream_diagnostics(video_manager, self.worker_source_id)
                return None
        else:
            logging.error(f"❌ Timed out after {max_wait_time}s waiting for first frame from {self.worker_source_id}.")
            self._log_stream_diagnostics(video_manager, self.worker_source_id)
            return None

    def _handle_frame_failure(self, video_manager, worker_source_id):
        """Handle frame retrieval failures with progressive backoff and recovery attempts."""
        self.consecutive_frame_failures += 1
        
        if not video_manager.has_stream(worker_source_id):
            logging.info(f"🛑 Stream {worker_source_id} was removed, stopping pipeline")
            return False
        
        time_since_last_frame = time.time() - self.last_successful_frame_time
        if time_since_last_frame > self.stream_recovery_timeout:
            logging.error(f"❌ Stream {worker_source_id} recovery timeout ({self.stream_recovery_timeout}s). Stopping pipeline.")
            return False
        
        if self.consecutive_frame_failures <= 10:
            if self.consecutive_frame_failures % 5 == 1:
                logging.debug(f"⚠️ No frame for {worker_source_id} (attempt {self.consecutive_frame_failures})")
            time.sleep(0.01)
        elif self.consecutive_frame_failures <= 50:
            if self.consecutive_frame_failures % 10 == 1:
                logging.warning(f"⚠️ No frame for {worker_source_id} (attempt {self.consecutive_frame_failures}). Stream may be reconnecting...")
            time.sleep(0.05)
        elif self.consecutive_frame_failures <= self.max_consecutive_failures:
            if self.consecutive_frame_failures % 20 == 1:
                logging.warning(f"⚠️ Persistent frame issues for {worker_source_id} (attempt {self.consecutive_frame_failures}). Checking stream health...")
                self._log_stream_diagnostics(video_manager, worker_source_id)
                if self.consecutive_frame_failures % 60 == 1:
                    if self._should_attempt_hevc_recovery(video_manager, worker_source_id):
                        logging.info("🔧 Attempting HEVC-specific recovery for persistent frame failures...")
                        if self._handle_hevc_recovery(video_manager, worker_source_id):
                            logging.info("✅ HEVC recovery successful, continuing pipeline...")
                            return True
            time.sleep(0.1)
        else:
            logging.error(f"❌ Too many consecutive frame failures for {worker_source_id} ({self.consecutive_frame_failures}). Stopping pipeline.")
            self._log_stream_diagnostics(video_manager, worker_source_id)
            return False
        
        return True
    
    def _log_stream_diagnostics(self, video_manager, worker_source_id):
        try:
            stream_url = video_manager.get_stream_url(worker_source_id)
            is_file = video_manager.is_video_file(worker_source_id)
            if hasattr(video_manager, 'streams') and worker_source_id in video_manager.streams:
                stream = video_manager.streams[worker_source_id]
                state = stream.get_state() if hasattr(stream, 'get_state') else "unknown"
                is_connected = stream.is_connected() if hasattr(stream, 'is_connected') else "unknown"
                
                logging.info(f"📊 Stream diagnostics for {worker_source_id}:")
                logging.info(f"   URL: {stream_url}")
                logging.info(f"   Type: {'Video file' if is_file else 'Live stream'}")
                logging.info(f"   State: {state}")
                logging.info(f"   Connected: {is_connected}")
                logging.info(f"   Time since last frame: {time.time() - self.last_successful_frame_time:.1f}s")
                
                if hasattr(stream, 'get_codec_info'):
                    codec_info = stream.get_codec_info()
                    if codec_info:
                        logging.info(f"   Codec: {codec_info}")
                        if 'hevc' in str(codec_info).lower() or 'h265' in str(codec_info).lower():
                            logging.warning("   ⚠️ HEVC stream detected - potential QP/POC errors")
                
                if hasattr(stream, 'get_recent_errors'):
                    recent_errors = stream.get_recent_errors()
                    if recent_errors:
                        hevc_errors = [err for err in recent_errors if 'cu_qp_delta' in str(err.get('error', '')) or 'Could not find ref with POC' in str(err.get('error', ''))]
                        if hevc_errors:
                            logging.warning(f"   🔥 Recent HEVC errors: {len(hevc_errors)}")
                            self.hevc_error_count += len(hevc_errors)
                            for i, err in enumerate(hevc_errors[-3:]):
                                logging.warning(f"   🔥 HEVC Error {i+1}: {err.get('error', '')[:100]}...")
            else:
                logging.info(f"📊 Stream {worker_source_id} not found in registry; checking device directly...")
        except Exception as e:
            logging.error(f"Error getting stream diagnostics: {e}")

    def _should_attempt_hevc_recovery(self, video_manager, worker_source_id) -> bool:
        current_time = time.time()
        if current_time - self.last_hevc_recovery < self.hevc_recovery_cooldown:
            logging.debug(f"HEVC recovery on cooldown ({current_time - self.last_hevc_recovery:.1f}s elapsed)")
            return False
        
        if hasattr(video_manager, 'streams') and worker_source_id in video_manager.streams:
            stream = video_manager.streams[worker_source_id]
            if hasattr(stream, 'get_recent_errors'):
                recent_errors = stream.get_recent_errors(max_age_seconds=60)
                hevc_errors = [err for err in recent_errors if 
                               'cu_qp_delta' in str(err.get('error', '')) or 
                               'Could not find ref with POC' in str(err.get('error', ''))]
                if len(hevc_errors) >= 3:
                    logging.info(f"HEVC recovery warranted: {len(hevc_errors)} HEVC errors in last minute")
                    return True
        
        if self.hevc_error_count >= 5:
            logging.info(f"HEVC recovery warranted: {self.hevc_error_count} total HEVC errors detected")
            return True
        
        return False

    def _handle_hevc_recovery(self, video_manager, worker_source_id):
        try:
            self.last_hevc_recovery = time.time()
            logging.info(f"🔧 Attempting HEVC stream recovery for {worker_source_id}")
            stream_url = video_manager.get_stream_url(worker_source_id)
            if not stream_url:
                logging.error(f"   Cannot get stream URL for {worker_source_id}")
                return False
            
            video_manager.remove_stream(worker_source_id)
            time.sleep(1.0)
            video_manager.add_stream(worker_source_id, stream_url)
            time.sleep(2.0)
            
            if not video_manager.has_stream(worker_source_id):
                logging.error(f"   Failed to recreate stream {worker_source_id}")
                return False
            
            self.reset_frame_failure_counters()
            self.hevc_error_count = 0
            logging.info(f"✅ HEVC recovery attempt completed for {worker_source_id}")
            return True
        except Exception as e:
            logging.error(f"❌ HEVC recovery failed for {worker_source_id}: {e}")
            return False

    def stop(self):
        """Stops the Pipeline processor and cleans up resources."""
        if not self.running:
            return
        logging.info("🛑 Stopping PipelineProcessor...")
        self.running = False

        if hasattr(self, 'rtmp_streamer') and self.rtmp_streamer:
            try:
                self.rtmp_streamer.stop_stream()
            except Exception as e:
                logging.error(f"Error stopping RTMP streamer: {e}")
            finally:
                self.rtmp_streamer = None

        try:
            while True:
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
        except Exception as e:
            logging.error(f"Error clearing frame queue: {e}")

        if self.detection_thread and self.detection_thread.is_alive():
            try:
                self.detection_thread.join(timeout=5.0)
                if self.detection_thread.is_alive():
                    logging.warning("Detection thread did not terminate cleanly")
            except Exception as e:
                logging.error(f"Error joining detection thread: {e}")
            finally:
                self.detection_thread = None

        self.tracked_objects_render.clear()

        try:
            if hasattr(self, 'video_debugger'):
                self.video_debugger.close_all()
        except Exception as e:
            logging.error(f"Error closing video debugger: {e}")

        logging.info("✅ PipelineProcessor stopped successfully")
        
    def _get_detection_interval(self):
        config = self.config_manager.get_feature_config("processing_speed")
        fps = config.get("decimal", 1.0)
        if fps <= 0:
            return 1.0 / 10.0  # default 10 fps
        return 1.0 / fps

    def enable_debug(self):
        self.debug_flag = True
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()
    
    def reset_frame_failure_counters(self):
        logging.info(f"🔄 Resetting frame failure counters for pipeline {self.pipeline_id}")
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()
        self.hevc_error_count = 0
    
    def get_hevc_diagnostics(self, video_manager) -> dict:
        diagnostics = {
            'hevc_error_count': self.hevc_error_count,
            'last_hevc_recovery': self.last_hevc_recovery,
            'time_since_last_recovery': time.time() - self.last_hevc_recovery,
            'recovery_cooldown_remaining': max(0, self.hevc_recovery_cooldown - (time.time() - self.last_hevc_recovery)),
            'consecutive_failures': self.consecutive_frame_failures,
            'time_since_last_frame': time.time() - self.last_successful_frame_time,
        }
        if hasattr(video_manager, 'streams') and self.worker_source_id in video_manager.streams:
            stream = video_manager.streams[self.worker_source_id]
            if hasattr(stream, 'get_codec_info'):
                diagnostics['codec'] = stream.get_codec_info()
            if hasattr(stream, 'get_recent_errors'):
                recent_errors = stream.get_recent_errors(max_age_seconds=300)
                hevc_errors = [err for err in recent_errors if 
                               'cu_qp_delta' in str(err.get('error', '')) or 
                               'Could not find ref with POC' in str(err.get('error', ''))]
                diagnostics['recent_hevc_errors'] = len(hevc_errors)
                diagnostics['total_recent_errors'] = len(recent_errors)
        return diagnostics