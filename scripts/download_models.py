#!/usr/bin/env python3
"""
Utility script for downloading pre-trained YOLO models
"""
import os
import logging
from pathlib import Path
from ultralytics import YOLO
from app.config.config import MODELS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_models():
    """Download pre-trained YOLO models"""
    models = ['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x']
    
    logger.info(f"Downloading models to {MODELS_DIR}")
    
    for model_name in models:
        try:
            logger.info(f"Downloading {model_name}...")
            model = YOLO(f"{model_name}.pt")
            logger.info(f"✓ {model_name} downloaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to download {model_name}: {str(e)}")
    
    logger.info("Model download complete")
    logger.info(f"Models saved to: {MODELS_DIR}")


if __name__ == '__main__':
    download_models()
