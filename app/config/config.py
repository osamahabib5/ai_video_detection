"""
Configuration settings for the video object detection system
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
APP_DIR = PROJECT_ROOT / 'app'
DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'
MODELS_DIR = DATA_DIR / 'models'
VIDEOS_DIR = DATA_DIR / 'videos'

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Model Configuration
MODEL_CONFIG = {
    'model_name': 'yolov8m',  # YOLOv8 medium model
    'model_path': str(MODELS_DIR / 'yolov8m.pt'),
    'confidence_threshold': 0.45,
    'iou_threshold': 0.50,
    'max_detections': 100,
}

# Video Processing Configuration
VIDEO_CONFIG = {
    'input_source': 0,  # 0 for webcam, or path to video file
    'frame_rate': 30,
    'frame_width': 1280,
    'frame_height': 720,
    'buffer_size': 30,
    'skip_frames': 1,  # Process every nth frame
}

# Detection Configuration
DETECTION_CONFIG = {
    'classes': None,  # None for all classes, or list of specific class IDs
    'agnostic_nms': False,
    'max_time_threshold': 5.0,  # Max processing time per frame
}

# Output Configuration
OUTPUT_CONFIG = {
    'save_results': True,
    'output_format': 'json',  # json, csv, or both
    'annotate_frames': True,
    'output_directory': str(LOGS_DIR / 'predictions'),
    'video_output': False,
    'video_output_path': str(LOGS_DIR / 'output_video.mp4'),
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': str(LOGS_DIR / 'app.log'),
    'max_bytes': 10485760,  # 10MB
    'backup_count': 5,
}

# Database Configuration (optional)
DATABASE_CONFIG = {
    'enabled': False,
    'type': 'sqlite',  # sqlite, postgresql, mysql
    'path': str(DATA_DIR / 'detections.db'),
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'device': 'cuda',  # cuda, cpu, or mps (Apple Silicon)
    'batch_size': 1,
    'half_precision': False,  # Use FP16
    'workers': 4,
}

# Streaming Configuration
STREAMING_CONFIG = {
    'enabled': False,
    'stream_url': 'rtsp://example.com/stream',  # RTSP URL
    'reconnect_attempts': 5,
    'reconnect_delay': 5,
}
