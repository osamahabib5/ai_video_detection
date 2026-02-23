"""
FastAPI REST API for video detection
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import tempfile
from pathlib import Path
import asyncio
from app.main import PredictionEngine
from app.utils.logger import Logger

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Detection API",
    description="Real-time object detection API",
    version="1.0.0"
)

# Initialize prediction engine
engine = PredictionEngine()
logger = Logger.get_logger(__name__)

# Request/Response models
class DetectionResponse(BaseModel):
    """Detection response model"""
    frame_id: int
    timestamp: str
    detections: list
    detection_count: int


class SummaryResponse(BaseModel):
    """Summary response model"""
    total_frames_processed: int
    total_detections: int
    average_detections_per_frame: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model_loaded: bool


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model_loaded=engine.detector.model is not None
    )


@app.post("/detect/file")
async def detect_video_file(file: UploadFile = File(...)):
    """
    Process uploaded video file
    
    Returns:
        JSON with detection results
    """
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process video
        result = engine.process_video(video_source=tmp_path)
        
        # Cleanup
        Path(tmp_path).unlink()
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/detect/webcam")
async def detect_webcam(max_frames: int = 100):
    """
    Process webcam stream
    
    Args:
        max_frames: Maximum frames to process
    
    Returns:
        JSON with detection results
    """
    try:
        result = engine.process_video(video_source=0, max_frames=max_frames)
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error processing webcam: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/stream")
async def detect_stream(stream_url: str, max_frames: int = 100):
    """
    Process RTSP stream
    
    Args:
        stream_url: RTSP stream URL
        max_frames: Maximum frames to process
    
    Returns:
        JSON with detection results
    """
    try:
        result = engine.process_video(video_source=stream_url, max_frames=max_frames)
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error processing stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{frame_id}")
async def get_detection_result(frame_id: int):
    """Get detection result for specific frame"""
    for result in engine.video_processor.results_buffer if engine.video_processor else []:
        if result['frame_id'] == frame_id:
            return JSONResponse(content=result)
    
    raise HTTPException(status_code=404, detail="Frame not found")


@app.get("/summary", response_model=SummaryResponse)
async def get_summary():
    """Get processing summary"""
    if not engine.results_manager:
        raise HTTPException(status_code=400, detail="No results available")
    
    summary = engine.results_manager.get_summary()
    return SummaryResponse(**summary)


@app.get("/download/results")
async def download_results(format: str = "json"):
    """Download results file"""
    if not engine.results_manager:
        raise HTTPException(status_code=400, detail="No results available")
    
    if format == "json":
        file_path = engine.results_manager.save_json()
        return FileResponse(file_path, media_type="application/json")
    elif format == "csv":
        file_path = engine.results_manager.save_csv()
        return FileResponse(file_path, media_type="text/csv")
    else:
        raise HTTPException(status_code=400, detail="Invalid format")


@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "available_models": [
            "yolov8n",
            "yolov8s",
            "yolov8m",
            "yolov8l",
            "yolov8x"
        ],
        "current_model": "yolov8m",
        "classes": len(engine.detector.get_class_names())
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Shutting down API")
    engine.shutdown()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
