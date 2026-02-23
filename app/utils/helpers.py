"""
Helper utilities for video processing and detection
"""
import cv2
import numpy as np
from datetime import datetime
import json
from pathlib import Path


class FrameProcessor:
    """Process and annotate frames"""
    
    @staticmethod
    def draw_detections(frame, detections, class_names=None):
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detection results
            class_names: List of class names
        
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = map(int, detection['bbox'])
            conf = detection['confidence']
            class_id = detection['class_id']
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Prepare label
            if class_names and class_id < len(class_names):
                label = f"{class_names[class_id]}: {conf:.2f}"
            else:
                label = f"Class {class_id}: {conf:.2f}"
            
            # Put text
            cv2.putText(
                annotated, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        
        return annotated
    
    @staticmethod
    def resize_frame(frame, width, height):
        """Resize frame to specified dimensions"""
        return cv2.resize(frame, (width, height))
    
    @staticmethod
    def get_frame_timestamp():
        """Get current timestamp"""
        return datetime.now().isoformat()


class ResultsManager:
    """Manage detection results storage and output"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    def add_result(self, frame_id, timestamp, detections):
        """Add detection result"""
        result = {
            'frame_id': frame_id,
            'timestamp': timestamp,
            'detections': detections,
            'detection_count': len(detections)
        }
        self.results.append(result)
    
    def save_json(self, filename='detections.json'):
        """Save results to JSON file"""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=4)
        return str(output_path)
    
    def save_csv(self, filename='detections.csv'):
        """Save results to CSV file"""
        import csv
        output_path = self.output_dir / filename
        
        if not self.results:
            return str(output_path)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['frame_id', 'timestamp', 'class_id', 'confidence', 'bbox'])
            
            for result in self.results:
                for detection in result['detections']:
                    writer.writerow([
                        result['frame_id'],
                        result['timestamp'],
                        detection['class_id'],
                        detection['confidence'],
                        ','.join(map(str, detection['bbox']))
                    ])
        
        return str(output_path)
    
    def get_summary(self):
        """Get summary statistics"""
        total_frames = len(self.results)
        total_detections = sum(r['detection_count'] for r in self.results)
        avg_detections = total_detections / total_frames if total_frames > 0 else 0
        
        return {
            'total_frames_processed': total_frames,
            'total_detections': total_detections,
            'average_detections_per_frame': avg_detections
        }


class MetricsCollector:
    """Collect and track performance metrics"""
    
    def __init__(self):
        self.frame_times = []
        self.inference_times = []
        self.total_frames = 0
    
    def add_frame_time(self, elapsed_time):
        """Add frame processing time"""
        self.frame_times.append(elapsed_time)
        self.total_frames += 1
    
    def add_inference_time(self, elapsed_time):
        """Add model inference time"""
        self.inference_times.append(elapsed_time)
    
    def get_metrics(self):
        """Get performance metrics"""
        if not self.frame_times:
            return {}
        
        return {
            'total_frames_processed': self.total_frames,
            'avg_frame_time_ms': np.mean(self.frame_times) * 1000,
            'avg_inference_time_ms': np.mean(self.inference_times) * 1000 if self.inference_times else 0,
            'fps': self.total_frames / sum(self.frame_times) if sum(self.frame_times) > 0 else 0,
            'total_processing_time_s': sum(self.frame_times)
        }
