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
    # 'yolo' = standard YOLOv8 (80 COCO classes)
    # 'yolo-world' = open-vocabulary YOLO-World (any custom classes)
    'model_type': 'yolo-world',
    'model_name': 'yolov8s-world.pt',  # 's'=fast CPU, 'm'/'l'/'x' for accuracy
    'model_path': str(MODELS_DIR / 'yolov8s-world.pt'),
    'confidence_threshold': 0.35,
    'iou_threshold': 0.45,
    'max_detections': 100,
    # Custom classes for YOLO-World (warehouse safety detection)
    'custom_classes': [
        'person', 'hardhat', 'helmet',
        'safety vest', 'high-visibility vest',
        'box', 'cardboard box', 'package',
        'forklift', 'pallet jack',
    ],
}

# Safety Compliance Configuration
SAFETY_CONFIG = {
    'enabled': True,                         # Enable/disable safety compliance checking
    'require_hardhat': True,                  # Alert if person near no hardhat
    'require_vest': True,                     # Alert if person near no safety vest
    'check_lifting': True,                    # Check lifting posture (needs pose model)
    'alert_webhook_url': None,                # Slack/Teams webhook URL (optional)
    'save_violations': True,                  # Save violations to JSON and CSV
    'output_directory': str(LOGS_DIR / 'violations'),  # Violation output directory
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
    'classes': None, # None for all COCO classes, or e.g., [0] for only people
    'agnostic_nms': False,
    'max_time_threshold': 5.0,
    # --- Class Name Filter (for standard YOLOv8 mode) ---
    # 'filter_mode': 'allow'  → keep ONLY classes in filter_list
    # 'filter_mode': 'deny'   → remove classes in filter_list
    # 'filter_mode': None     → no filtering (default)
    # NOT needed when using YOLO-World (custom_classes handles it natively)
    'filter_mode': None,
    'filter_list': [],
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