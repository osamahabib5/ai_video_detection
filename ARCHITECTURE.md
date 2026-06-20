# System Architecture Design

## Overview

The AI Video Detection System is a production-ready ML pipeline for real-time object detection from video feeds.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Video Input Sources                           │
│  (Webcam / Video File / RTSP Stream / REST API)                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VideoCapture Layer                            │
│  - Frame extraction                                             │
│  - Resolution handling                                          │
│  - Frame buffering                                              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              VideoProcessor (Pipeline Orchestrator)              │
│  - Frame scheduling                                             │
│  - Callback management                                          │
│  - Processing flow control                                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   [Detection]   [Annotation]   [Results Manager]
        │               │               │
        ▼               ▼               ▼
┌──────────────────────────────────────────────────────┐
│          ObjectDetector (YOLOv8)                     │
│  - Model inference                                  │
│  - Box parsing                                      │
│  - Confidence filtering                             │
│  - Class mapping                                    │
└──────────┬───────────────────────────────────────────┘
           │
        ┌──┴──────────────────────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│  FrameProcessor      │              │  ResultsManager      │
│  - Draw boxes        │              │  - Store detections  │
│  - Add labels        │              │  - Export JSON/CSV   │
│  - Annotate frames   │              │  - Generate summary  │
└──────────────────────┘              └──────────────────────┘
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│  VideoWriter         │              │  MetricsCollector    │
│  - Output video      │              │  - Track timing      │
│  - Encode frames     │              │  - Calculate FPS     │
│  - Save annotated    │              │  - Performance stats │
│    video             │              │                      │
└──────────────────────┘              └──────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              Output Layer                           │
│  - Video files (annotated)                         │
│  - JSON results                                    │
│  - CSV exports                                     │
│  - Application logs                                │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### Frame Processing Pipeline

```
Input Frame
    ↓
[VideoCapture] → Reads frame from source
    ↓
[Frame Preprocessing] → Resize if needed
    ↓
[ObjectDetector] → YOLOv8 inference
    ↓
[Result Parsing] → Extract boxes, confidence, class
    ↓
[FrameProcessor] → Draw annotations
    ↓
[Results Storage] → Save to JSON/CSV
    ↓
[Output] → Annotated frame + Detection data
```

## Component Details

### 1. Configuration Layer (`app/config/config.py`)
- Centralized configuration management
- Model parameters
- Video settings
- Output options
- Logging setup
- Database configuration

### 2. Core Components

#### ObjectDetector (`app/detectors/yolo_detector.py`)
```
Input: Video frame (numpy array)
↓
[Load YOLO Model] → YOLOv8m (configurable)
↓
[Run Inference] → PyTorch forward pass
↓
[Parse Results] → Extract bounding boxes
↓
[Filter Results] → Apply confidence threshold
↓
Output: List of detections
```

**Features:**
- Multi-device support (CUDA, CPU, MPS)
- Configurable confidence threshold
- NMS filtering
- Class filtering
- Performance monitoring

#### VideoProcessor (`app/video_processing/video_processor.py`)
```
Input: Video source (0, file path, or stream URL)
↓
[VideoCapture] → Initialize video source
↓
[Frame Read Loop]
  ├── Read frame
  ├── Validate frame
  ├── Skip if configured
  └── Process frame
↓
[Callback System] → Execute processing
↓
Output: List of detections per frame
```

**Features:**
- Multi-source support
- Frame skipping for performance
- Callback-based processing
- Error handling
- Progress tracking

#### FrameProcessor (`app/utils/helpers.py`)
- Draw bounding boxes
- Add confidence scores
- Label annotations
- Timestamp overlay

#### ResultsManager (`app/utils/helpers.py`)
- Collect detection results
- Export to JSON
- Export to CSV
- Generate summaries

#### MetricsCollector (`app/utils/helpers.py`)
- Track processing times
- Calculate FPS
- Collect performance data
- Generate metrics report

### 3. Logger (`app/utils/logger.py`)
- Rotating file handler
- Console output
- Structured logging
- Multiple log levels

### 4. API Layer (`app/api.py`)
- FastAPI REST endpoints
- File upload handling
- Webcam processing
- Stream processing
- Results download
- Model info endpoint

## Technology Stack

### Core ML/CV
- **PyTorch**: Deep learning framework
- **YOLOv8**: Object detection model
- **OpenCV**: Video processing

### Web Framework
- **FastAPI**: REST API
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Infrastructure
- **venv**: Python virtual environment isolation

### Data Processing
- **NumPy**: Numerical computing
- **Pandas**: Data analysis
- **Python-dotenv**: Environment variables

## Performance Characteristics

### Memory Usage
- Model: ~100-300MB (depends on model size)
- Inference: ~50-150MB per batch
- Buffer: Configurable

### Processing Speed
- **yolov8n**: ~50-80 FPS (GPU), 5-10 FPS (CPU)
- **yolov8m**: ~20-40 FPS (GPU), 2-5 FPS (CPU)
- **yolov8l**: ~10-20 FPS (GPU), 1-3 FPS (CPU)

### Latency
- Inference time: 10-100ms per frame (GPU)
- Total processing: 20-150ms per frame

## Scalability Considerations

### Vertical Scaling
1. Use larger GPU (A100 vs V100)
2. Increase batch size
3. Use faster models (yolov8n)

### Horizontal Scaling
1. Multiple instances with load balancer
2. Message queue (RabbitMQ, Redis)
3. Distributed processing

### Optimization Techniques
1. Frame skipping
2. Lower resolution processing
3. Model quantization
4. Batch processing
5. Asynchronous processing

## Deployment Modes

### Development
```
Local environment → Python interpreter → Logs to console
```

### Production (CPU)
```
venv → Local Python interpreter → Direct file access
```

### Production (GPU)
```
venv + CUDA PyTorch → GPU acceleration → Direct file access
```

### Cloud Deployment
```
Kubernetes cluster → Multiple replicas → Auto-scaling → Monitoring
```

## Security Considerations

1. **Input Validation**
   - File size limits
   - Format validation
   - Stream authentication

2. **Resource Management**
   - Container limits
   - Timeout mechanisms
   - Memory constraints

3. **Data Protection**
   - Encrypted logs
   - Secure API endpoints
   - Access control

4. **Model Security**
   - Model versioning
   - Integrity checks
   - Update mechanisms

## Monitoring & Logging

### Metrics Tracked
- FPS (Frames Per Second)
- Inference latency
- Memory usage
- GPU utilization
- Error rates

### Log Levels
- **DEBUG**: Detailed information
- **INFO**: General information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical failures

### Health Checks
- Model availability
- GPU/CPU status
- Memory availability
- Inference capability

## Error Handling

### Level 1: Input Validation
- Check source availability
- Validate frame properties
- Verify model loaded

### Level 2: Processing
- Catch inference errors
- Handle incomplete frames
- Timeout protection

### Level 3: Output
- Validate results format
- Check storage space
- Verify exports

## Future Enhancements

1. **Multi-Model Support**
   - Ensemble detection
   - Specialized models per class
   - Dynamic model selection

2. **Advanced Features**
   - Object tracking
   - Scene understanding
   - Anomaly detection

3. **Optimization**
   - Model compression
   - Edge deployment
   - Real-time inference

4. **Integration**
   - Message queues
   - Database backends
   - Monitoring systems

---

**Architecture Version**: 1.0
**Last Updated**: February 4, 2024
