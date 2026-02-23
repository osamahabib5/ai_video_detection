"""
Unit tests for the video detection system
"""
import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock


class TestObjectDetector(unittest.TestCase):
    """Test ObjectDetector class"""
    
    @patch('app.detectors.yolo_detector.YOLO')
    def test_model_loading(self, mock_yolo):
        """Test model initialization"""
        from app.detectors.yolo_detector import ObjectDetector
        
        mock_yolo.return_value = MagicMock()
        detector = ObjectDetector()
        
        self.assertIsNotNone(detector.model)
    
    def test_detection_parsing(self):
        """Test detection result parsing"""
        # This would need actual model output
        pass


class TestVideoProcessor(unittest.TestCase):
    """Test VideoProcessor class"""
    
    def test_video_capture_initialization(self):
        """Test video capture setup"""
        from app.video_processing.video_processor import VideoCapture
        
        with patch('cv2.VideoCapture'):
            capture = VideoCapture(0)
            self.assertIsNotNone(capture)


class TestHelpers(unittest.TestCase):
    """Test helper functions"""
    
    def test_frame_processor(self):
        """Test frame annotation"""
        from app.utils.helpers import FrameProcessor
        
        # Create dummy frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        detections = [
            {
                'bbox': [100, 100, 200, 200],
                'confidence': 0.95,
                'class_id': 0
            }
        ]
        
        annotated = FrameProcessor.draw_detections(frame, detections)
        self.assertEqual(annotated.shape, frame.shape)
    
    def test_results_manager(self):
        """Test results management"""
        from app.utils.helpers import ResultsManager
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ResultsManager(tmpdir)
            manager.add_result(0, "2024-02-04T10:30:00", [])
            
            summary = manager.get_summary()
            self.assertEqual(summary['total_frames_processed'], 1)


if __name__ == '__main__':
    unittest.main()
