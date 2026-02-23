"""
Main application entry point - Optimized for Docker & CPU Inference
"""
import time
import sys
from pathlib import Path
from app.utils.logger import Logger
from app.utils.helpers import FrameProcessor, ResultsManager, MetricsCollector
from app.detectors.yolo_detector import ObjectDetector
from app.video_processing.video_processor import VideoProcessor, VideoWriter
from app.config.config import VIDEO_CONFIG, OUTPUT_CONFIG


class PredictionEngine:
    """Main prediction engine orchestrating the entire pipeline"""
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.detector = None
        self.video_processor = None
        self.results_manager = None
        self.metrics_collector = None
        self.initialize()
    
    def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Prediction Engine...")
        
        # Initialize detector - Ensure it's in Predict mode
        self.detector = ObjectDetector()
        
        # Initialize results manager
        output_dir = Path(OUTPUT_CONFIG['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        self.results_manager = ResultsManager(str(output_dir))
        
        # Initialize metrics collector
        self.metrics_collector = MetricsCollector()
        
        self.logger.info("Prediction Engine initialized successfully")
    
    def process_video(self, video_source=0, max_frames=None):
        """
        Process video and detect objects in Inference Mode
        """
        self.logger.info(f"Starting video processing from source: {video_source}")
        
        # Initialize video processor
        self.video_processor = VideoProcessor(self.detector, video_source)
        
        # Initialize video writer if output is enabled
        video_writer = None
        if OUTPUT_CONFIG['annotate_frames'] and OUTPUT_CONFIG['video_output']:
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
        
        try:
            # Process video (ensure detector.predict is used inside .process)
            self.video_processor.process(callback=frame_callback, max_frames=max_frames)
            
            # Save results
            self.logger.info("Saving results...")
            json_path = self.results_manager.save_json()
            
            if OUTPUT_CONFIG['output_format'] in ['csv', 'both']:
                self.results_manager.save_csv()
            
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


def main():
    """Main application entry point"""
    logger = Logger.get_logger(__name__)
    logger.info("Starting AI Video Detection System")
    
    try:
        engine = PredictionEngine()
        
        # --- DOCKER VOLUME PATH LOGIC ---
        # Look for a video file in the mounted data directory
        video_input_dir = Path("/app/data/videos")
        video_files = list(video_input_dir.glob("*.mp4")) + list(video_input_dir.glob("*.avi"))
        
        if video_files:
            source = str(video_files[0])
            logger.info(f"Auto-detected video file: {source}")
        else:
            logger.warning("No video files found in /app/data/videos. Falling back to webcam (Device 0).")
            source = 0 
            
        # Run inference (set max_frames to None to process the whole video)
        result = engine.process_video(video_source=source, max_frames=200)
        
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