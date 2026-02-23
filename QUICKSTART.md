# Quick Start Guide for AI Video Detection

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose installed
- 4GB+ RAM
- GPU (optional)

### 5-Minute Setup

#### Step 1: Navigate to project
```bash
cd ai_video_detection
```

#### Step 2: Build Docker image
```bash
docker build -t ai-video-detection:latest .
```

#### Step 3: Start container
```bash
docker-compose up -d
```

#### Step 4: Process video (choose one)

**Option A: Webcam**
```bash
docker-compose exec video-detection python -m app.main
```

**Option B: Video file**
```bash
# Copy video to data/videos/
docker-compose exec video-detection python -m app.main
# Edit app/config/config.py: VIDEO_CONFIG['input_source'] = 'path/to/video.mp4'
```

**Option C: Using API**
```bash
# Start API server
docker-compose exec video-detection python -m uvicorn app.api:app --host 0.0.0.0 --port 8000

# Upload video
curl -X POST -F "file=@video.mp4" http://localhost:8000/detect/file
```

## 📁 Directory Structure

```
ai_video_detection/
├── app/                          # Main application
│   ├── main.py                  # Entry point (PredictionEngine)
│   ├── api.py                   # FastAPI REST API
│   ├── config/
│   │   └── config.py            # All configuration
│   ├── detectors/
│   │   └── yolo_detector.py     # YOLOv8 detector
│   ├── video_processing/
│   │   └── video_processor.py   # Video capture & processing
│   ├── utils/
│   │   ├── logger.py            # Logging setup
│   │   └── helpers.py           # Helper functions
│   └── models/                  # Custom model architectures
├── data/
│   ├── models/                  # Pre-trained weights
│   └── videos/                  # Input videos
├── logs/
│   └── predictions/             # Output results (JSON/CSV)
├── scripts/
│   ├── download_models.py       # Download YOLO models
│   ├── generate_sample_video.py # Create test video
│   └── test_system.py           # System test
├── tests/
│   └── test_detection.py        # Unit tests
├── Dockerfile                    # Standard image
├── docker-compose.yml           # Docker Compose config
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
├── QUICKSTART.md               # This file
├── Makefile                     # Make commands
├── start.sh / start.bat        # Quick start scripts
└── cleanup.sh / cleanup.bat    # Cleanup scripts
```

## 🎯 Common Tasks

### Download YOLO Models
```bash
python scripts/download_models.py
```

### Generate Test Video
```bash
python scripts/generate_sample_video.py
```

### Run Tests
```bash
pytest tests/
```

### View Configuration
```bash
cat app/config/config.py
```

### Monitor Container
```bash
docker stats ai-video-detection
docker logs -f ai-video-detection
```

## ⚙️ Configuration

### Quick Config Changes
Edit `app/config/config.py`:

```python
# Change model
MODEL_CONFIG['model_name'] = 'yolov8n'  # Faster

# Change device
PERFORMANCE_CONFIG['device'] = 'cuda'  # Use GPU

# Change confidence threshold
MODEL_CONFIG['confidence_threshold'] = 0.5

# Skip frames for speed
VIDEO_CONFIG['skip_frames'] = 2  # Process every 2nd frame
```

## 📊 Output Files

Results are saved in `logs/predictions/`:

- `detections.json` - All detections in JSON format
- `detections.csv` - CSV format for spreadsheet analysis
- `output_video.mp4` - Annotated video (if enabled)
- `app.log` - Application logs

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of Memory | Reduce frame size or skip frames |
| Low FPS | Use smaller model (yolov8n) or skip frames |
| Docker build fails | `docker system prune` to clean cache |
| GPU not detected | Install nvidia-docker |

## 📈 Performance Tips

1. **Skip Frames**: Set `skip_frames: 2` to process every 2nd frame
2. **Smaller Model**: Use `yolov8n` instead of `yolov8x`
3. **Lower Resolution**: Reduce `frame_width` and `frame_height`
4. **Enable GPU**: Set `device: 'cuda'` (NVIDIA) or `'mps'` (Apple)
5. **Batch Processing**: Set `batch_size > 1` for multiple frames

## 🌐 API Endpoints

If running FastAPI server:

- `GET /health` - Health check
- `POST /detect/file` - Upload video file
- `GET /detect/webcam` - Process webcam
- `GET /detect/stream` - Process RTSP stream
- `GET /summary` - Get results summary
- `GET /download/results` - Download results
- `GET /models` - List available models

## 📚 Next Steps

1. Read [README.md](README.md) for detailed documentation
2. Check [app/config/config.py](app/config/config.py) for all options
3. Review [app/main.py](app/main.py) to understand the pipeline
4. Explore API in [app/api.py](app/api.py)

## 🤝 Support

- Check logs: `docker logs ai-video-detection`
- Review config: `app/config/config.py`
- Run test: `python scripts/test_system.py`
- Check README.md for detailed guide

---

**Happy Detecting! 🎯**
