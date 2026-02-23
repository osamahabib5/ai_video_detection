#!/usr/bin/env python3
"""
Test the detection system with a sample frame
"""
import cv2
import numpy as np
from pathlib import Path
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import PredictionEngine
from app.utils.logger import Logger


def test_system():
    """Run system test"""
    logger = Logger.get_logger(__name__)
    logger.info("Starting system test...")
    
    try:
        # Initialize engine
        logger.info("Initializing prediction engine...")
        engine = PredictionEngine()
        
        # Create test frame
        logger.info("Creating test frame...")
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        test_frame[100:400, 100:400] = [0, 255, 0]  # Green square
        
        # Test prediction
        logger.info("Running prediction on test frame...")
        detections = engine.predict_single_frame(test_frame)
        
        logger.info(f"Test complete. Detections: {len(detections)}")
        
        for det in detections:
            logger.info(f"  - {det['class_name']}: {det['confidence']:.2f}")
        
        # Shutdown
        engine.shutdown()
        
        logger.info("✓ System test passed!")
        return True
    
    except Exception as e:
        logger.error(f"✗ System test failed: {str(e)}")
        return False


if __name__ == '__main__':
    success = test_system()
    exit(0 if success else 1)
