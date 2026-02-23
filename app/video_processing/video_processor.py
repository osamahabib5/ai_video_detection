"""
Video Processing Module
"""
import cv2
import time
from typing import Optional, Callable
from app.utils.logger import Logger
from app.config.config import VIDEO_CONFIG, OUTPUT_CONFIG


class VideoCapture:
    """Handle video capture from various sources"""
    
    def __init__(self, source: int | str = 0):
        """
        Initialize video capture
        
        Args:
            source: 0 for webcam, or path to video file
        """
        self.logger = Logger.get_logger(__name__)
        self.source = source
        self.cap = None
        self.is_open = False
        self.frame_count = 0
        self._initialize_capture()
    
    def _initialize_capture(self):
        """Initialize the video capture object"""
        try:
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open video source: {self.source}")
                return
            
            # Set video properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_CONFIG['frame_width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_CONFIG['frame_height'])
            self.cap.set(cv2.CAP_PROP_FPS, VIDEO_CONFIG['frame_rate'])
            
            self.is_open = True
            self.logger.info(f"Video source initialized: {self.source}")
            
        except Exception as e:
            self.logger.error(f"Error initializing video capture: {str(e)}")
    
    def read_frame(self):
        """
        Read next frame
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.is_open:
            return False, None
        
        success, frame = self.cap.read()
        
        if success:
            self.frame_count += 1
        
        return success, frame
    
    def get_properties(self):
        """Get video properties"""
        if not self.is_open:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'total_frames': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'current_frame': self.frame_count
        }
    
    def release(self):
        """Release video capture"""
        if self.cap:
            self.cap.release()
            self.is_open = False
            self.logger.info("Video capture released")


class VideoProcessor:
    """Process video frames through detection pipeline"""
    
    def __init__(self, detector, source: int | str = 0):
        """
        Initialize video processor
        
        Args:
            detector: ObjectDetector instance
            source: Video source (0 for webcam or file path)
        """
        self.logger = Logger.get_logger(__name__)
        self.detector = detector
        self.video_capture = VideoCapture(source)
        self.frame_count = 0
        self.results_buffer = []
    
    def process(self, 
                callback: Optional[Callable] = None,
                max_frames: Optional[int] = None) -> list:
        """
        Process video frames through detection pipeline
        
        Args:
            callback: Optional callback function for each frame
            max_frames: Maximum frames to process (None for all)
        
        Returns:
            List of all detections
        """
        all_detections = []
        skip_frames = VIDEO_CONFIG['skip_frames']
        
        if not self.video_capture.is_open:
            self.logger.error("Video source not open")
            return all_detections
        
        self.logger.info("Starting video processing...")
        
        try:
            while True:
                success, frame = self.video_capture.read_frame()
                
                if not success:
                    self.logger.info("End of video stream")
                    break
                
                # Skip frames if configured
                if self.frame_count % skip_frames != 0:
                    self.frame_count += 1
                    continue
                
                # Check max frames
                if max_frames and self.frame_count >= max_frames:
                    break
                
                start_time = time.time()
                
                # Run detection
                detections, inference_time = self.detector.predict(frame)
                
                processing_time = time.time() - start_time
                
                # Store results
                frame_result = {
                    'frame_id': self.frame_count,
                    'detections': detections,
                    'inference_time': inference_time,
                    'total_processing_time': processing_time
                }
                
                all_detections.append(frame_result)
                self.results_buffer.append(frame_result)
                
                # Call callback if provided
                if callback:
                    callback(frame, detections, frame_result)
                
                # Log progress
                if self.frame_count % 30 == 0:
                    self.logger.info(
                        f"Processed {self.frame_count} frames | "
                        f"Detections: {len(detections)} | "
                        f"Inference: {inference_time*1000:.2f}ms"
                    )
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            self.logger.info("Processing interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during processing: {str(e)}")
        finally:
            self.cleanup()
        
        self.logger.info(f"Processing complete. Total frames: {self.frame_count}")
        return all_detections
    
    def cleanup(self):
        """Cleanup resources"""
        self.video_capture.release()
        self.logger.info("Cleanup complete")


class VideoWriter:
    """Write annotated video"""
    
    def __init__(self, output_path: str, fps: float = 30, frame_size: tuple = (1280, 720)):
        """
        Initialize video writer
        
        Args:
            output_path: Output video file path
            fps: Frames per second
            frame_size: (width, height)
        """
        self.logger = Logger.get_logger(__name__)
        self.output_path = output_path
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        
        if not self.writer.isOpened():
            self.logger.error(f"Failed to open video writer: {output_path}")
        else:
            self.logger.info(f"Video writer initialized: {output_path}")
    
    def write_frame(self, frame):
        """Write frame to video"""
        if self.writer.isOpened():
            self.writer.write(frame)
    
    def release(self):
        """Release video writer"""
        if self.writer:
            self.writer.release()
            self.logger.info(f"Video saved: {self.output_path}")
