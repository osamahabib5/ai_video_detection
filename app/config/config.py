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
(LOGS_DIR / 'predictions').mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Model Configuration
MODEL_CONFIG = {
    'model_name': 'yolov8m',
    'model_path': str(MODELS_DIR / 'yolov8m.pt'),
    'confidence_threshold': 0.50, # Slightly higher to reduce "Truck" false positives
    'iou_threshold': 0.50,
    'max_detections': 100,
}

# Video Processing Configuration
VIDEO_CONFIG = {
    # CHANGE THIS: Use a local path, a direct URL, or a device index (0 for webcam)
    'input_source': 0,
    'frame_rate': 30,
    'frame_width': 1280,
    'frame_height': 720,
    'buffer_size': 30,
    'skip_frames': 2, # Skip every other frame to help CPU keep up with web streams
}

# Detection Configuration
DETECTION_CONFIG = {
    'classes': None, # None for all, or e.g., [0] for only people
    'agnostic_nms': False,
    'max_time_threshold': 5.0,
}

# Output Configuration
OUTPUT_CONFIG = {
    'save_results': True,
    'output_format': 'json',
    'annotate_frames': True,
    'output_directory': str(LOGS_DIR / 'predictions'),
    'video_output': True, # ENABLED
    'video_output_path': str(LOGS_DIR / 'predictions' / 'output_result.avi'), # Saved as .avi for XVID
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': str(LOGS_DIR / 'app.log'),
    'max_bytes': 10485760,
    'backup_count': 5,
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'device': 'cpu', # Use 'cuda' if you have an NVIDIA GPU with CUDA PyTorch installed
    'batch_size': 1,
    'half_precision': False,
    'workers': 4,
}