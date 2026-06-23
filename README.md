# AI Video Detection System — Warehouse Safety Edition

Real-time warehouse safety compliance monitoring using YOLO-World. Detects PPE violations (missing hardhat/vest) and unsafe lifting posture, with automatic alert generation.

## Overview

This system:
- **Detects workers, PPE, and equipment** in warehouse video feeds
- **Checks compliance** — hardhat, safety vest, safe lifting posture
- **Generates alerts** for violations (console, JSON, CSV, webhook)
- **Saves results** in JSON/CSV format
- **Runs in a Python virtual environment** for easy deployment

## Overview

This is a production-ready ML system that:
- **Processes live video feeds** from webcams or video files
- **Detects objects** using YOLOv8 neural network
- **Generates predictions** with bounding boxes and confidence scores
- **Saves results** in JSON/CSV format
- **Runs in a Python virtual environment** for easy deployment

## Project Structure

```
ai_video_detection/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py          # Configuration settings
│   ├── detectors/
│   │   ├── __init__.py
│   │   └── yolo_detector.py   # YOLO-based detector
│   ├── video_processing/
│   │   ├── __init__.py
│   │   └── video_processor.py # Video capture and processing
│   ├── models/                # Custom model architectures (optional)
│   │   └── __init__.py
│   ├── safety/                # Warehouse safety compliance
│   │   ├── __init__.py
│   │   ├── compliance_checker.py  # PPE & posture rule checks
│   │   └── alert_manager.py       # Violation logging & alerts
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Logging utilities
│       └── helpers.py         # Helper functions
├── data/
│   ├── models/                # Pre-trained model weights
│   └── videos/                # Input video files
├── logs/
│   └── predictions/           # Output predictions
├── tests/                      # Unit tests
├── requirements.txt           # Python dependencies
├── setup.sh / setup.bat       # Venv setup scripts
├── start.sh / start.bat       # Quick start scripts
├── cleanup.sh / cleanup.bat   # Cleanup scripts
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Features

### Core Features
- ✅ Real-time warehouse worker detection
- ✅ PPE compliance: hardhat/helmet + safety vest checks
- ✅ Unsafe lifting posture detection (with YOLOv8-pose)
- ✅ Automatic violation alerts (console, JSON, CSV, webhook-ready)
- ✅ Frame annotation with bounding boxes + violation warnings
- ✅ Performance metrics and logging
- ✅ Python virtual environment (venv) isolation

### Advanced Features
- 🔧 Batch processing capability
- 🔧 Custom model support
- 🔧 GPU acceleration (CUDA, MPS)
- 🔧 REST API endpoint
- 🔧 Database integration (optional)
- 🔧 Real-time monitoring dashboards

## Installation

### Prerequisites
- Python 3.10+
- 4GB+ RAM
- GPU (optional, for faster processing)

### Quick Start

#### 1. Setup Virtual Environment
```bash
cd ai_video_detection
# On Linux/macOS or Windows (Git Bash / WSL):
bash setup.sh
# On Windows (Command Prompt / PowerShell):
setup.bat
```

#### 2. Activate Environment
```bash
# On Linux/macOS or WSL:
source venv/bin/activate
# On Windows (Git Bash):
source venv/Scripts/activate
# On Windows (Command Prompt / PowerShell):
venv\Scripts\activate
```

#### 3. Process Video
```bash
python -m app.main
```

Or use the quick start script:
```bash
# On Linux/macOS:
bash start.sh
# On Windows:
start.bat
```

## Usage

### Basic Usage (Webcam)

```python
from app.main import PredictionEngine

# Initialize engine
engine = PredictionEngine()

# Process webcam stream
result = engine.process_video(video_source=0, max_frames=300)

# Print results
print(result['summary'])
print(result['metrics'])

# Shutdown
engine.shutdown()
```

### Process Video File

```python
engine = PredictionEngine()

# Process video file
result = engine.process_video(
    video_source='path/to/video.mp4',
    max_frames=None  # Process entire video
)
```

### Predict on Single Frame

```python
import cv2

frame = cv2.imread('image.jpg')
detections = engine.predict_single_frame(frame)

for detection in detections:
    print(f"Class: {detection['class_name']}")
    print(f"Confidence: {detection['confidence']:.2f}")
    print(f"BBox: {detection['bbox']}")
```

## Configuration

Edit `app/config/config.py` to customize:

### Model Configuration
```python
MODEL_CONFIG = {
    'model_type': 'yolo-world',         # 'yolo' (80 COCO classes) or 'yolo-world' (open-vocabulary)
    'model_name': 'yolov8s-world.pt',   # 's'=fast, 'm'=balanced, 'l'/'x'=accurate
    'confidence_threshold': 0.40,
    'iou_threshold': 0.45,
    'max_detections': 100,
    'custom_classes': ['squirrel', 'bird', 'sparrow'],  # ← YOLO-World: ANY classes you want!
}
```

> **🎯 YOLO-World** detects ANY object you name — no training required. Just list your classes in `custom_classes` and the model finds them. Switch back to standard YOLOv8 by setting `model_type: 'yolo'` with `model_name: 'yolov8m'`.

### Video Configuration
```python
VIDEO_CONFIG = {
    'input_source': 0,  # Webcam
    'frame_rate': 30,
    'frame_width': 1280,
    'frame_height': 720,
    'skip_frames': 1,  # Process every frame
}
```

### Detection Configuration
```python
DETECTION_CONFIG = {
    'classes': None,  # None = all, or e.g. [0, 14] for person+bird only (YOLOv8 only)
    'agnostic_nms': False,
    'max_time_threshold': 5.0,
    'filter_mode': None,     # 'allow' | 'deny' | None — class filter (for YOLOv8 mode)
    'filter_list': [],       # Class names to allow/deny
}
```

> **💡 YOLO-World vs standard YOLOv8**:
> - **YOLO-World** (`model_type: 'yolo-world'`): set `custom_classes` in MODEL_CONFIG, detects ONLY those
> - **YOLOv8** (`model_type: 'yolo'`): 80 COCO classes only, use `filter_list` to narrow results

### Safety Compliance Configuration
```python
SAFETY_CONFIG = {
    'enabled': True,                     # Enable safety checks
    'require_hardhat': True,            # Alert if worker has no hardhat nearby
    'require_vest': True,               # Alert if worker has no safety vest nearby
    'check_lifting': True,              # Check lifting posture (with pose model)
    'alert_webhook_url': None,          # Slack/Teams webhook for real-time alerts
    'save_violations': True,            # Save violations to logs/violations/
}
```

### Output Configuration
```python
OUTPUT_CONFIG = {
    'save_results': True,
    'output_format': 'json',
    'annotate_frames': True,
    'output_directory': 'logs/predictions',
}
```

### Performance Configuration
```python
PERFORMANCE_CONFIG = {
    'device': 'cuda',  # cuda, cpu, mps
    'batch_size': 1,
    'half_precision': False,
}
```

## Virtual Environment Usage

### Setup
```bash
# On Linux/macOS or Windows (Git Bash / WSL):
bash setup.sh

# On Windows (Command Prompt / PowerShell):
setup.bat
```

### Activate Environment
```bash
# On Linux/macOS or WSL:
source venv/bin/activate

# On Windows (Git Bash):
source venv/Scripts/activate

# On Windows (Command Prompt / PowerShell):
venv\Scripts\activate
```

### Run Application
```bash
# Process webcam (default)
python -m app.main

# Process video file
python -m app.main path/to/video.mp4

# Process RTSP stream
python -m app.main rtsp://your-stream-url
```

### Start API Server
```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

### GPU Support (NVIDIA)
```bash
# Install PyTorch with CUDA support instead of CPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Then set device to 'cuda' in app/config/config.py
```

## Output Files

After processing, outputs are saved in `logs/predictions/`:

### detections.json
```json
[
  {
    "frame_id": 0,
    "timestamp": "2024-02-04T10:30:45.123456",
    "detections": [
      {
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.95,
        "bbox": [100.5, 200.3, 350.8, 500.2],
        "area": 45000.0
      }
    ],
    "detection_count": 1
  }
]
```

### detections.csv
```
frame_id,timestamp,class_id,class_name,confidence,bbox
0,2024-02-04T10:30:45.123456,0,person,0.95,"100.5,200.3,350.8,500.2"
```

### objects_detected.csv (unique classes only)
```
class_name,class_id,total_detections,avg_confidence,min_confidence,max_confidence
person,0,450,0.912,0.689,0.987
bird,14,120,0.784,0.512,0.921
```

## Performance Metrics

The system tracks:
- **FPS**: Frames per second
- **Inference Time**: Model prediction time per frame
- **Processing Time**: Total time per frame
- **Memory Usage**: RAM and VRAM utilization (if GPU)

Example output:
```
{
  "total_frames_processed": 300,
  "avg_frame_time_ms": 45.2,
  "avg_inference_time_ms": 35.8,
  "fps": 22.1,
  "total_processing_time_s": 13.56
}
```

## Logging

Logs are saved to `logs/app.log`:

```
2024-02-04 10:30:45,123 - app.main - INFO - Starting AI Video Detection System
2024-02-04 10:30:46,456 - app.detectors.yolo_detector - INFO - Loading model: yolov8m
2024-02-04 10:30:50,789 - app.detectors.yolo_detector - INFO - Model loaded successfully
2024-02-04 10:30:51,234 - app.video_processing.video_processor - INFO - Starting video processing...
```

## Advanced Features

### Custom Model Integration

Add custom detectors in `app/detectors/`:

```python
class CustomDetector:
    def predict(self, frame):
        # Your detection logic
        return detections, inference_time
```

### REST API Integration

Create `app/api.py`:

```python
from fastapi import FastAPI
from app.main import PredictionEngine

app = FastAPI()
engine = PredictionEngine()

@app.post("/predict")
def predict(frame_path: str):
    # Prediction logic
    pass
```

### Database Storage

Enable in `config.py`:

```python
DATABASE_CONFIG = {
    'enabled': True,
    'type': 'postgresql',
    'path': 'postgresql://user:password@db:5432/detections'
}
```

## Troubleshooting

### Issue: Out of Memory
**Solution**: Reduce batch size or frame resolution in config

### Issue: Low FPS
**Solution**: Skip frames, use smaller model (yolov8n), or enable GPU

### Issue: Dependency Installation Fails
**Solution**: Ensure Python 3.10+ is installed, then re-run `bash setup.sh`

### Issue: No GPU Detected
**Solution**: Install CUDA-compatible PyTorch: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

## Environment Variables

Create `.env` file:

```bash
MODEL_DEVICE=cuda
CONFIDENCE_THRESHOLD=0.45
FRAME_RATE=30
LOG_LEVEL=INFO
```

## Testing

```bash
# Run tests with venv activated
python -m pytest tests/ -v
```

## Performance Optimization

1. **Skip Frames**: Process every Nth frame
2. **Resize Input**: Lower resolution = faster processing
3. **Use Smaller Model**: yolov8n vs yolov8x
4. **Enable GPU**: 10x+ speedup with CUDA
5. **Batch Processing**: Process multiple frames together

## Monitoring

Monitor resource usage:

```bash
# Monitor with htop/top on Linux, or Task Manager on Windows
# View application logs
tail -f logs/app.log
```

## Security Considerations

1. Use `.env` for sensitive data
2. Run in an isolated virtual environment (venv)
3. Use environment variables via `.env` file
4. Keep dependencies updated: `pip list --outdated`
5. Review code for security best practices

## Contributing

1. Create feature branch
2. Implement changes
3. Add tests
4. Submit pull request

## License

[Your License Here]

## Support

- 📧 Email: support@example.com
- 📚 Documentation: /docs
- 🐛 Issues: GitHub Issues

## References

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)

---

**Last Updated**: February 4, 2024
**Version**: 1.0.0

## RTMP / Live Stream Usage

You can provide an RTMP/RTSP stream as the input source via a CLI argument or environment variable. When a live stream is detected (URLs starting with `rtmp://` or `rtsp://`), the application will process indefinitely by default (`max_frames=None`).

Examples:

- CLI (local run):

```bash
python -m app.main rtmp://localhost:1935/live/streamkey
```

- Environment variable (Linux/macOS):

```bash
export VIDEO_SOURCE="rtmp://your.server:1935/live/streamkey"
python -m app.main
```

- Environment variable (Windows PowerShell):

```powershell
$env:VIDEO_SOURCE = 'rtmp://your.server:1935/live/streamkey'
python -m app.main
```

- Virtual environment (pass env var):

```bash
export VIDEO_SOURCE='rtmp://your.server:1935/live/streamkey'
python -m app.main
```

Notes:

- You can also set `RTMP_URL` or `RTMP_SOURCE` environment variables; `VIDEO_SOURCE` takes precedence when present.
- Numeric strings (e.g. `"0"`) passed via CLI or env are coerced to integers and treated as webcam device indices.
- If you want to limit processing time on a stream, pass a numeric `max_frames` value by editing the call in `app/main.py` or subclassing `PredictionEngine`.
