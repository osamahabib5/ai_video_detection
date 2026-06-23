"""
Object Detection Module — YOLOv8 & YOLO-World Support
"""
import torch
from ultralytics import YOLO
import time
from app.utils.logger import Logger
from app.config.config import MODEL_CONFIG, PERFORMANCE_CONFIG, DETECTION_CONFIG


class ObjectDetector:
    """Object detector supporting standard YOLOv8 and open-vocabulary YOLO-World."""
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.model = None
        self.model_type = MODEL_CONFIG.get('model_type', 'yolo')
        self.device = self._get_device()
        self._class_filter = self._build_class_filter()
        self.load_model()
    
    def _build_class_filter(self):
        """Build a set of allowed class names from DETECTION_CONFIG filter.
        Not needed for YOLO-World (custom_classes handles it natively)."""
        if self.model_type == 'yolo-world':
            return None  # YOLO-World only detects custom_classes anyway
        filter_mode = DETECTION_CONFIG.get('filter_mode')
        filter_list = DETECTION_CONFIG.get('filter_list', [])
        if not filter_mode or not filter_list:
            return None
        filter_set = {name.lower() for name in filter_list}
        return {'mode': filter_mode, 'names': filter_set}
    
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
        """Load the YOLO model — standard or YOLO-World open-vocabulary."""
        try:
            model_name = MODEL_CONFIG['model_name']
            self.logger.info(f"Loading {self.model_type} model: {model_name}")
            
            self.model = YOLO(model_name)
            self.model.to(self.device)
            
            # --- YOLO-World: set custom classes ---
            if self.model_type == 'yolo-world':
                custom_classes = MODEL_CONFIG.get('custom_classes', [])
                if not custom_classes:
                    self.logger.warning(
                        "YOLO-World mode but 'custom_classes' is empty. "
                        "Add classes like ['squirrel', 'bird'] to MODEL_CONFIG."
                    )
                else:
                    self.model.set_classes(custom_classes)
                    self.logger.info(
                        f"YOLO-World custom classes: {', '.join(custom_classes)}"
                    )
            
            # Set to evaluation mode
            if hasattr(self.model, 'model') and self.model.model is not None:
                self.model.model.eval()
                
            self.logger.info(f"{self.model_type} model loaded successfully")
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
            class_name = result.names[class_id]
            
            # --- Apply class-name filter ---
            if self._class_filter is not None:
                name_lower = class_name.lower()
                mode = self._class_filter['mode']
                allowed = self._class_filter['names']
                if mode == 'allow' and name_lower not in allowed:
                    continue  # skip this detection
                elif mode == 'deny' and name_lower in allowed:
                    continue  # skip this detection
            
            detection = {
                'class_id': class_id,
                'class_name': class_name,
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