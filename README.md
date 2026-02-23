# AI Video Detection System

Real-time object detection system for video feeds using YOLOv8 and Docker.

## Overview

This is a production-ready ML system that:
- **Processes live video feeds** from webcams or video files
- **Detects objects** using YOLOv8 neural network
- **Generates predictions** with bounding boxes and confidence scores
- **Saves results** in JSON/CSV format
- **Runs in Docker** for easy deployment

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
├── Dockerfile                  # Standard Dockerfile
├── Dockerfile.advanced        # Advanced Dockerfile with GPU support
├── docker-compose.yml         # Docker compose configuration
├── requirements.txt           # Python dependencies
├── .dockerignore              # Docker ignore file
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Features

### Core Features
- ✅ Real-time object detection from video streams
- ✅ Support for multiple video sources (webcam, file, RTSP stream)
- ✅ Configurable detection thresholds
- ✅ Frame annotation with bounding boxes
- ✅ Result export (JSON, CSV)
- ✅ Performance metrics and logging
- ✅ Docker containerization

### Advanced Features
- 🔧 Batch processing capability
- 🔧 Custom model support
- 🔧 GPU acceleration (CUDA, MPS)
- 🔧 REST API endpoint
- 🔧 Database integration (optional)
- 🔧 Real-time monitoring dashboards

## Installation

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM
- GPU (optional, for faster processing)

### Quick Start

#### 1. Clone and Setup
```bash
cd ai_video_detection
```

#### 2. Build Docker Image
```bash
docker build -t ai-video-detection:latest .
```

#### 3. Run Container
```bash
docker-compose up
```

#### 4. Process Video
```bash
docker-compose exec video-detection python -m app.main
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
    'model_name': 'yolov8m',
    'confidence_threshold': 0.45,
    'iou_threshold': 0.50,
    'max_detections': 100,
}
```

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
    'classes': None,  # All classes
    'agnostic_nms': False,
    'max_time_threshold': 5.0,
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

## Docker Usage

### Build Image
```bash
# Standard build
docker build -t ai-video-detection:latest .

# Advanced build with GPU support
docker build -f Dockerfile.advanced -t ai-video-detection:gpu --build-arg ENABLE_GPU=true .
```

### Run Container
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Manual run
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ai-video-detection:latest
```

### Process Webcam (Linux)
```bash
docker run -it \
  --device /dev/video0:/dev/video0 \
  -v $(pwd)/logs:/app/logs \
  ai-video-detection:latest
```

### GPU Support (NVIDIA)
```bash
# Uncomment GPU lines in docker-compose.yml
# Requires nvidia-docker

docker-compose up
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
frame_id,timestamp,class_id,confidence,bbox
0,2024-02-04T10:30:45.123456,0,0.95,"100.5,200.3,350.8,500.2"
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

### Issue: Docker Build Fails
**Solution**: Ensure sufficient disk space, clear Docker cache: `docker system prune`

### Issue: No GPU Detected
**Solution**: Install nvidia-docker, uncomment GPU lines in docker-compose.yml

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
# Run tests inside container
docker-compose exec video-detection pytest tests/

# Or locally
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
docker stats ai-video-detection
```

## Security Considerations

1. Use `.env` for sensitive data
2. Limit container resources (see docker-compose.yml)
3. Run as non-root user
4. Use read-only volumes when possible
5. Scan images for vulnerabilities: `trivy image ai-video-detection:latest`

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
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: February 4, 2024
**Version**: 1.0.0
