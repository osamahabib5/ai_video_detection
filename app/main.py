"""
Main application entry point — Warehouse Safety Detection System
"""
import time
import sys
import os
import cv2
from pathlib import Path
from app.utils.logger import Logger
from app.utils.helpers import FrameProcessor, ResultsManager, MetricsCollector
from app.detectors.yolo_detector import ObjectDetector
from app.video_processing.video_processor import VideoProcessor, VideoWriter
from app.safety.compliance_checker import ComplianceChecker
from app.safety.alert_manager import AlertManager
from app.utils.youtube_fetcher import YouTubeFetcher
from app.identification.person_db import PersonDB
from app.identification.face_recognizer import FaceRecognizer
from app.identification.enrollment_gui import EnrollmentGUI
from app.config.config import (
    VIDEO_CONFIG, OUTPUT_CONFIG, VIDEOS_DIR, SAFETY_CONFIG, IDENTIFICATION_CONFIG,
)


class PredictionEngine:
    """Main prediction engine — detection + safety compliance + alerts"""
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.detector = None
        self.video_processor = None
        self.results_manager = None
        self.metrics_collector = None
        self.compliance_checker = None
        self.alert_manager = None
        self.initialize()
    
    def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Warehouse Safety Detection Engine...")
        
        # Initialize detector
        self.detector = ObjectDetector()
        
        # Initialize results manager
        output_dir = Path(OUTPUT_CONFIG['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        self.results_manager = ResultsManager(str(output_dir))
        
        # Initialize metrics collector
        self.metrics_collector = MetricsCollector()
        
        # Initialize safety compliance (if enabled)
        if SAFETY_CONFIG.get('enabled', False):
            self.compliance_checker = ComplianceChecker(rules_config=SAFETY_CONFIG)
            violation_dir = Path(SAFETY_CONFIG.get('output_directory', 'logs/violations'))
            violation_dir.mkdir(parents=True, exist_ok=True)
            self.alert_manager = AlertManager(str(violation_dir), config=SAFETY_CONFIG)
            self.logger.info("Safety compliance monitoring ENABLED")
        else:
            self.logger.info("Safety compliance monitoring DISABLED")

        # Initialize face identification (if enabled)
        self.face_recognizer = None
        self.person_db = None
        self._current_person_id = None
        self._current_person_name = 'UNKNOWN'
        self._face_check_counter = 0
        self._face_interval = IDENTIFICATION_CONFIG.get('face_check_interval', 5)
        self._unknown_face_streak = 0         # consecutive unknown face checks
        self._unknown_enroll_offered = False  # only prompt once per session
        self._unknown_prompt_threshold = 10   # face checks before prompting (~5 sec at 2 FPS)

        if IDENTIFICATION_CONFIG.get('enabled', False):
            self.person_db = PersonDB(db_path=IDENTIFICATION_CONFIG.get('db_path', 'data/faces.db'))
            self.face_recognizer = FaceRecognizer(self.person_db)
            enrolled = self.person_db.count_enrolled()
            self.logger.info(f"Face identification ENABLED ({enrolled} persons enrolled)")

            # Auto-enroll if no one is enrolled
            if enrolled == 0 and IDENTIFICATION_CONFIG.get('auto_enroll_on_start', True):
                cam_idx = IDENTIFICATION_CONFIG.get('camera_index', 0)
                self.logger.info("No enrolled persons — launching enrollment GUI...")
                gui = EnrollmentGUI(self.face_recognizer, self.person_db, camera_index=cam_idx)
                gui.start()
                enrolled = self.person_db.count_enrolled()
                if enrolled > 0:
                    self.logger.info(f"Enrollment complete: {enrolled} person(s) now in database")
                else:
                    self.logger.warning("No persons enrolled — face ID will skip")
        else:
            self.logger.info("Face identification DISABLED")
        
        self.logger.info("Prediction Engine initialized successfully")
    
    def process_video(self, video_source=0, max_frames=None):
        """
        Process video and detect objects in Inference Mode
        """
        self.logger.info(f"Starting video processing from source: {video_source}")
        
        # Initialize video processor
        self.video_processor = VideoProcessor(self.detector, video_source)
        
        # Detect if this is a live camera (webcam, iPhone via Camo, etc.)
        is_live = self.video_processor.is_live_camera
        
        # Initialize video writer only for file sources (not live cameras)
        video_writer = None
        if not is_live and OUTPUT_CONFIG['annotate_frames'] and OUTPUT_CONFIG['video_output']:
            video_writer = VideoWriter(
                OUTPUT_CONFIG['video_output_path'],
                VIDEO_CONFIG['frame_rate'],
                (VIDEO_CONFIG['frame_width'], VIDEO_CONFIG['frame_height'])
            )
        
        def frame_callback(frame, detections, frame_result):
            """Callback for each processed frame"""
            # Annotate frame
            annotated_frame = FrameProcessor.draw_detections(
                frame, 
                detections, 
                list(self.detector.get_class_names().values())
            )
            
            # Write annotated frame to video
            if video_writer:
                video_writer.write_frame(annotated_frame)
            
            # Store results
            timestamp = FrameProcessor.get_frame_timestamp()
            self.results_manager.add_result(
                frame_result['frame_id'],
                timestamp,
                detections
            )
            
            # Track metrics
            self.metrics_collector.add_frame_time(frame_result['total_processing_time'])
            self.metrics_collector.add_inference_time(frame_result['inference_time'])

            # --- Face identification (every Nth frame) ---
            if self.face_recognizer is not None:
                self._face_check_counter += 1
                if self._face_check_counter >= self._face_interval:
                    self._face_check_counter = 0
                    pid, pname, pconf, face_bbox = self.face_recognizer.identify(frame)
                    if pname not in ('NO_FACE_DETECTED', 'NOT_ENROLLED'):
                        self._current_person_id = pid
                        self._current_person_name = pname
                        self._unknown_face_streak = 0  # reset — known person
                    elif pname == 'NO_FACE_DETECTED':
                        self._current_person_name = 'NO_FACE'
                        self._unknown_face_streak = 0
                    elif pname == 'UNKNOWN_PERSON':
                        self._current_person_name = 'UNKNOWN_PERSON'
                        self._unknown_face_streak += 1
                        # --- Prompt to enroll unknown face ---
                        if (self._unknown_face_streak >= self._unknown_prompt_threshold
                                and not self._unknown_enroll_offered
                                and self.person_db.count_enrolled() > 0):
                            self._unknown_enroll_offered = True
                            # Pause processing briefly and show dialog
                            import tkinter.messagebox as tkmb
                            enroll = tkmb.askyesno(
                                "Unknown Face Detected",
                                "A face has been detected that doesn't match any "
                                "enrolled person.\n\n"
                                "Would you like to enroll this person now?\n\n"
                                "Click 'Yes' to open the enrollment window.\n"
                                "Click 'No' to continue — they will be labeled as 'UNKNOWN_PERSON'."
                            )
                            if enroll:
                                self._unknown_face_streak = 0
                                self._unknown_enroll_offered = False
                                cam_idx = IDENTIFICATION_CONFIG.get('camera_index',
                                    int(self.video_processor.source) if isinstance(self.video_processor.source, (int, str)) and str(self.video_processor.source).isdigit() else 0)
                                gui = EnrollmentGUI(self.face_recognizer, self.person_db, camera_index=cam_idx)
                                gui.start()
                                self.logger.info("Enrollment dialog closed — resuming monitoring")
                            else:
                                self.logger.info("Unknown person enrollment declined — labeling as UNKNOWN_PERSON")

                    # Draw face box if identified
                    if face_bbox and IDENTIFICATION_CONFIG.get('highlight_face', True):
                        x, y, w, h = face_bbox
                        if pname == 'UNKNOWN_PERSON':
                            color = (0, 165, 255)  # orange
                        elif pname in ('NO_FACE_DETECTED',):
                            color = (0, 0, 255)     # red
                        else:
                            color = (0, 255, 0)      # green — known person
                        cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                        label = f"{pname} ({pconf:.2f})" if pconf > 0 else pname
                        cv2.putText(annotated_frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # --- Safety compliance check ---
            if self.compliance_checker and detections:
                violations = self.compliance_checker.check_frame(
                    detections, frame_shape=frame.shape[:2])
                if violations:
                    # Attach person identity to each violation
                    for v in violations:
                        v['person_name'] = self._current_person_name
                        v['person_id'] = self._current_person_id or ''
                    self.alert_manager.add_violations(
                        frame_result['frame_id'],
                        FrameProcessor.get_frame_timestamp(),
                        violations
                    )
                    annotated_frame = FrameProcessor.draw_violation_warnings(
                        annotated_frame, violations
                    )
            
            # --- Live preview window (for webcam/iPhone mode) ---
            if hasattr(self.video_processor, 'is_live_camera') and self.video_processor.is_live_camera:
                # Add FPS overlay
                fps_text = f"FPS: {1.0 / max(frame_result['total_processing_time'], 0.001):.1f}"
                cv2.putText(annotated_frame, fps_text, (10, annotated_frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imshow('AI Video Detection — Live', annotated_frame)
        
        try:
            # Process video (ensure detector.predict is used inside .process)
            self.video_processor.process(callback=frame_callback, max_frames=max_frames)
            
            # Save results
            self.logger.info("Saving results...")
            json_path = self.results_manager.save_json()
            
            if OUTPUT_CONFIG['output_format'] in ['csv', 'both']:
                self.results_manager.save_csv()
            
            # Always save the unique-objects summary
            objects_csv_path = self.results_manager.save_objects_summary()
            self.logger.info(f"Unique objects summary saved to: {objects_csv_path}")
            
            # Save safety violations if enabled
            if self.alert_manager and SAFETY_CONFIG.get('save_violations', True):
                violations_json = self.alert_manager.save_violations_json()
                violations_csv = self.alert_manager.save_violations_csv()
                violation_summary = self.alert_manager.get_summary()
                self.logger.info(
                    f"Safety violations: {violation_summary['total_violations']} total | "
                    f"{violation_summary['by_type']}"
                )
            
            summary = self.results_manager.get_summary()
            metrics = self.metrics_collector.get_metrics()
            
            if video_writer:
                video_writer.release()
            
            return {
                'success': True,
                'summary': summary,
                'metrics': metrics,
                'results_file': json_path
            }
        
        except Exception as e:
            self.logger.error(f"Error during video processing: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def shutdown(self):
        """Shutdown the engine"""
        self.logger.info("Shutting down Prediction Engine...")
        if self.detector:
            self.detector.unload_model()
        self.logger.info("Shutdown complete")

    def predict_single_frame(self, frame):
        """Run detection on a single frame (no video loop)."""
        detections, inference_time = self.detector.predict(frame)
        return detections


def main():
    """Main application entry point"""
    logger = Logger.get_logger(__name__)
    logger.info("Starting AI Video Detection System")
    
    try:
        engine = PredictionEngine()
        
        # Determine video source: CLI arg, ENV vars, mounted files, or webcam
        env_source = os.environ.get('VIDEO_SOURCE') or os.environ.get('RTMP_URL') or os.environ.get('RTMP_SOURCE')
        cli_source = None
        if len(sys.argv) > 1:
            cli_source = sys.argv[1]

        if cli_source:
            source = cli_source
            logger.info(f"Using CLI video source: {source}")
        elif env_source:
            source = env_source
            logger.info(f"Using environment video source: {source}")
        else:
            # Look for a video file in the local data/videos directory
            video_input_dir = VIDEOS_DIR
            video_files = list(video_input_dir.glob("*.mp4")) + list(video_input_dir.glob("*.avi"))
            
            if video_files:
                source = str(video_files[0])
                logger.info(f"Auto-detected video file: {source}")
            else:
                logger.warning(f"No video files found in {VIDEOS_DIR}. Falling back to webcam (Device 0).")
                source = 0

        # Coerce numeric strings to int (e.g., "0") for webcam device indexes
        if isinstance(source, str) and source.isdigit():
            source = int(source)

        # --- YouTube video handling ---
        youtube_fetcher = YouTubeFetcher(output_dir=str(VIDEOS_DIR))
        if isinstance(source, str) and youtube_fetcher.is_youtube_url(source):
            logger.info(f"YouTube URL detected. Downloading video...")
            downloaded = youtube_fetcher.fetch(source)
            if downloaded:
                source = downloaded
                logger.info(f"YouTube video downloaded to: {source}")
            else:
                logger.error("Failed to download YouTube video. Exiting.")
                sys.exit(1)

        # If using a live stream (rtmp/rtsp) or webcam, process indefinitely
        is_live = (
            isinstance(source, int) or
            (isinstance(source, str) and (
                source.startswith("rtmp://") or
                source.startswith("rtsp://") or
                source.isdigit()
            ))
        )
        max_frames = None if is_live else 200

        result = engine.process_video(video_source=source, max_frames=max_frames)
        
        if result['success']:
            logger.info(f"Success! Summary: {result['summary']}")
        else:
            logger.error(f"Failed: {result['error']}")
        
        engine.shutdown()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()