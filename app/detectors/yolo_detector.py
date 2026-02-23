"""
Object Detection Module using YOLO
"""
import torch
from ultralytics import YOLO
import time
from app.utils.logger import Logger
from app.config.config import MODEL_CONFIG, DETECTION_CONFIG, PERFORMANCE_CONFIG


class ObjectDetector:
    """YOLO-based object detector"""
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.model = None
        self.device = self._get_device()
        self.load_model()
    
    def _get_device(self):
        """Determine available device"""
        device = PERFORMANCE_CONFIG['device']
        
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
        """Load the YOLO model"""
        try:
            self.logger.info(f"Loading model: {MODEL_CONFIG['model_name']}")
            self.model = YOLO(MODEL_CONFIG['model_name'])
            self.model.to(self.device)
            
            # Set model to evaluation mode
            self.model.eval()
            
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def predict(self, frame):
        """
        Run inference on a frame
        
        Args:
            frame: Input frame (numpy array)
        
        Returns:
            Tuple of (detections, inference_time)
        """
        start_time = time.time()
        
        try:
            # Run inference
            with torch.no_grad():
                results = self.model(
                    frame,
                    conf=MODEL_CONFIG['confidence_threshold'],
                    iou=MODEL_CONFIG['iou_threshold'],
                    device=self.device,
                    verbose=False
                )
            
            inference_time = time.time() - start_time
            
            # Parse results
            detections = self._parse_results(results)
            
            return detections, inference_time
        
        except Exception as e:
            self.logger.error(f"Inference failed: {str(e)}")
            return [], time.time() - start_time
    
    def _parse_results(self, results):
        """
        Parse YOLO results into detections
        
        Args:
            results: YOLO model results
        
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        if len(results) == 0:
            return detections
        
        result = results[0]
        boxes = result.boxes
        
        for i, box in enumerate(boxes):
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
        
        # Sort by confidence
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Limit detections
        max_detections = MODEL_CONFIG['max_detections']
        detections = detections[:max_detections]
        
        return detections
    
    def get_class_names(self):
        """Get list of class names"""
        if self.model:
            return self.model.names
        return {}
    
    def unload_model(self):
        """Unload model and free memory"""
        if self.model:
            del self.model
            torch.cuda.empty_cache()
            self.logger.info("Model unloaded")
