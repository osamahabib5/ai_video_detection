"""
Object Detection Module using YOLO - Fixed for Inference
"""
import torch
from ultralytics import YOLO
import time
from app.utils.logger import Logger
from app.config.config import MODEL_CONFIG, PERFORMANCE_CONFIG


class ObjectDetector:
    """YOLO-based object detector optimized for inference"""
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.model = None
        self.device = self._get_device()
        self.load_model()
    
    def _get_device(self):
        """Determine available device"""
        device = PERFORMANCE_CONFIG.get('device', 'cpu')
        
        if device == 'cuda' and torch.cuda.is_available():
            self.logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
            return 'cuda'
        elif device == 'mps' and torch.backends.mps.is_available():
            self.logger.info("Using Apple Metal Performance Shaders (MPS)")
            return 'mps'
        else:
            self.logger.info("Using CPU for inference")
            return 'cpu'
    
    def load_model(self):
        """Load the YOLO model for inference mode"""
        try:
            self.logger.info(f"Loading model: {MODEL_CONFIG['model_name']}")
            # We explicitly load the model weights
            self.model = YOLO(MODEL_CONFIG['model_name'])
            
            # Move to device (CPU/GPU)
            self.model.to(self.device)
            
            # Set to evaluation mode to ensure no training logic runs
            if hasattr(self.model, 'model'):
                self.model.model.eval()
                
            self.logger.info("Model loaded successfully in evaluation mode")
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def predict(self, frame):
        """
        Run inference on a frame - FORCED PREDICT MODE
        """
        start_time = time.time()
        
        try:
            # We use .predict() specifically to avoid the "train" default
            with torch.no_grad():
                results = self.model.predict(
                    source=frame,
                    conf=MODEL_CONFIG['confidence_threshold'],
                    iou=MODEL_CONFIG.get('iou_threshold', 0.45),
                    device=self.device,
                    verbose=False  # This stops the training-style log spam
                )
            
            inference_time = time.time() - start_time
            detections = self._parse_results(results)
            
            return detections, inference_time
        
        except Exception as e:
            self.logger.error(f"Inference failed: {str(e)}")
            return [], time.time() - start_time
    
    def _parse_results(self, results):
        """Parse YOLO results into detections"""
        detections = []
        
        if not results or len(results) == 0:
            return detections
        
        result = results[0]
        boxes = result.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            
            detection = {
                'class_id': class_id,
                'class_name': result.names[class_id],
                'confidence': confidence,
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'bbox_width': float(x2 - x1),
                'bbox_height': float(y2 - y1),
                'area': float((x2 - x1) * (y2 - y1))
            }
            detections.append(detection)
        
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        max_dets = MODEL_CONFIG.get('max_detections', 50)
        return detections[:max_dets]
    
    def get_class_names(self):
        return self.model.names if self.model else {}
    
    def unload_model(self):
        if self.model:
            del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.logger.info("Model unloaded")