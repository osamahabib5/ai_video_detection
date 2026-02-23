# AI Video Detection System - Complete Directory Structure

```
📦 AI_VIDEO_DETECTION/
│
├── 📄 README.md                          # Main documentation
├── 📄 QUICKSTART.md                      # 5-minute quick start guide
├── 📄 ARCHITECTURE.md                    # System architecture & design
├── 📄 requirements.txt                   # Python dependencies (PyTorch, YOLOv8, etc.)
├── 📄 .gitignore                         # Git ignore rules
├── 📄 .dockerignore                      # Docker ignore rules
├── 📄 .env.example                       # Environment variables template
│
├── 🐳 DOCKER CONFIGURATION
│   ├── 📄 Dockerfile                     # Standard CPU/GPU Docker image
│   ├── 📄 Dockerfile.advanced            # Advanced multi-stage build with GPU support
│   ├── 📄 docker-compose.yml             # Docker Compose orchestration
│   ├── 📄 start.sh                       # Linux startup script
│   ├── 📄 start.bat                      # Windows startup script
│   ├── 📄 cleanup.sh                     # Linux cleanup script
│   ├── 📄 cleanup.bat                    # Windows cleanup script
│   └── 📄 Makefile                       # Make commands for easy management
│
├── 📁 APP/                               # Main application code
│   ├── 📄 __init__.py                    # Package initialization
│   ├── 📄 main.py                        # Main entry point (PredictionEngine)
│   ├── 📄 api.py                         # FastAPI REST API endpoints
│   │
│   ├── 📁 CONFIG/                        # Configuration module
│   │   ├── 📄 __init__.py
│   │   └── 📄 config.py                  # Central configuration (models, video, output, etc.)
│   │
│   ├── 📁 DETECTORS/                     # Object detection module
│   │   ├── 📄 __init__.py
│   │   └── 📄 yolo_detector.py           # YOLOv8 object detector implementation
│   │
│   ├── 📁 VIDEO_PROCESSING/              # Video processing module
│   │   ├── 📄 __init__.py
│   │   └── 📄 video_processor.py         # VideoCapture, VideoProcessor, VideoWriter
│   │
│   ├── 📁 UTILS/                         # Utility functions
│   │   ├── 📄 __init__.py
│   │   ├── 📄 logger.py                  # Logging configuration & setup
│   │   └── 📄 helpers.py                 # FrameProcessor, ResultsManager, MetricsCollector
│   │
│   └── 📁 MODELS/                        # Custom model architectures (optional)
│       └── 📄 __init__.py
│
├── 📁 DATA/                              # Data directory
│   ├── 📁 MODELS/                        # Pre-trained model weights
│   │   └── (YOLOv8 .pt files will be stored here)
│   │
│   └── 📁 VIDEOS/                        # Input video files
│       └── (Place your videos here)
│
├── 📁 LOGS/                              # Logs and outputs
│   ├── 📁 PREDICTIONS/                   # Detection results
│   │   ├── detections.json               # All detections in JSON format
│   │   ├── detections.csv                # All detections in CSV format
│   │   └── output_video.mp4              # Annotated output video (optional)
│   │
│   └── app.log                           # Application logs (rotating)
│
├── 📁 SCRIPTS/                           # Utility scripts
│   ├── 📄 __init__.py
│   ├── 📄 download_models.py             # Download YOLOv8 models
│   ├── 📄 generate_sample_video.py       # Generate sample video for testing
│   └── 📄 test_system.py                 # System integrity test
│
├── 📁 TESTS/                             # Unit tests
│   ├── 📄 __init__.py
│   └── 📄 test_detection.py              # Test cases for detection system
│
└── 📄 show_structure.py                  # Display project structure script
```

## 📊 Module Relationships

```
main.py (PredictionEngine)
    ├── ObjectDetector
    │   └── YOLO model (ultralytics)
    ├── VideoProcessor
    │   ├── VideoCapture
    │   ├── FrameProcessor
    │   └── VideoWriter
    ├── ResultsManager
    │   ├── save_json()
    │   └── save_csv()
    └── MetricsCollector
        └── get_metrics()

api.py (FastAPI)
    ├── /detect/file
    ├── /detect/webcam
    ├── /detect/stream
    ├── /summary
    ├── /download/results
    └── /health
```

## 🔧 Core Components Summary

### Configuration (`app/config/config.py`)
- MODEL_CONFIG: YOLOv8 settings
- VIDEO_CONFIG: Video processing settings
- DETECTION_CONFIG: Detection parameters
- OUTPUT_CONFIG: Output format options
- PERFORMANCE_CONFIG: Device & optimization
- LOGGING_CONFIG: Logger setup

### Detection (`app/detectors/yolo_detector.py`)
- ObjectDetector class
- Model loading & inference
- Result parsing
- Device management (CUDA/CPU/MPS)

### Video Processing (`app/video_processing/video_processor.py`)
- VideoCapture: Frame extraction
- VideoProcessor: Pipeline orchestration
- VideoWriter: Output video generation

### Utilities (`app/utils/`)
- Logger: Logging setup
- FrameProcessor: Annotation & visualization
- ResultsManager: Results storage & export
- MetricsCollector: Performance tracking

### API (`app/api.py`)
- FastAPI REST endpoints
- File upload & processing
- Stream processing
- Results download

## 🚀 Quick Start Paths

### For Users
1. Read: QUICKSTART.md
2. Run: `docker-compose up`
3. Process: `docker-compose exec video-detection python -m app.main`

### For Developers
1. Read: README.md + ARCHITECTURE.md
2. Review: app/config/config.py
3. Study: app/main.py (PredictionEngine)
4. Explore: app/detectors/yolo_detector.py
5. Extend: Create custom detectors

### For DevOps
1. Review: Dockerfile + docker-compose.yml
2. Check: requirements.txt
3. Setup: GPU support (nvidia-docker)
4. Monitor: docker stats, logs

## 📈 Data Flow Summary

```
Input Source (webcam/file/stream)
    ↓
VideoCapture (Frame extraction)
    ↓
VideoProcessor (Pipeline orchestration)
    ↓
ObjectDetector (YOLOv8 inference)
    ↓
FrameProcessor (Annotation)
    ↓
ResultsManager (Storage)
    ↓
Output Files (JSON/CSV/Video)
```

## 🎯 Key Features by File

| File | Purpose | Key Features |
|------|---------|--------------|
| config.py | Configuration | Centralized settings for all modules |
| yolo_detector.py | Detection | YOLOv8 inference, device support |
| video_processor.py | Video I/O | Multi-source support, frame processing |
| logger.py | Logging | Rotating logs, console output |
| helpers.py | Utilities | Annotation, results, metrics |
| main.py | Orchestration | Pipeline coordination |
| api.py | REST API | HTTP endpoints for processing |

## 🔄 Processing Pipeline

```
Configuration Loaded
    ↓
ObjectDetector Initialized
    ↓
VideoCapture Started
    ↓
For Each Frame:
    ├── Read Frame
    ├── Resize (optional)
    ├── Run Inference
    ├── Parse Results
    ├── Annotate Frame
    ├── Store Results
    └── Track Metrics
    ↓
Export Results (JSON/CSV)
    ↓
Generate Metrics Report
    ↓
Cleanup & Shutdown
```

## 📦 Dependencies Structure

```
pytorch
    ├── torch
    ├── torchvision
    └── torchaudio

ultralytics (YOLOv8)
    ├── Models
    ├── Inference
    └── Utils

opencv-python
    ├── Video I/O
    ├── Image Processing
    └── Annotation

fastapi (API)
    ├── REST endpoints
    ├── Request validation
    └── Response serialization

Supporting
    ├── numpy
    ├── pandas
    ├── scipy
    └── pyyaml
```

## 🎓 Learning Path

1. **Beginner**: Start with QUICKSTART.md
2. **Intermediate**: Read README.md and explore app/config/config.py
3. **Advanced**: Study ARCHITECTURE.md and review all module implementations
4. **Expert**: Modify detection logic, add custom models, deploy to cloud

---

**Project Structure Version**: 1.0
**Last Updated**: February 4, 2024
**Total Files**: 35+
**Lines of Code**: 2000+
