#!/usr/bin/env python3
"""Test YOLO-World with larger model and lower threshold."""
import sys, cv2
from pathlib import Path
from ultralytics import YOLO

video_dir = Path('data/videos')
video_files = list(video_dir.glob('*.mp4')) + list(video_dir.glob('*.avi'))
video_path = str(video_files[0]) if video_files else 'data/videos/video_animals.mp4'

# Try medium model (better CLIP embeddings)
for model_name in ['yolov8s-world.pt', 'yolov8m-world.pt']:
    print(f"\n{'='*60}")
    print(f"Testing {model_name}")
    print('='*60, flush=True)
    
    model = YOLO(model_name)
    cap = cv2.VideoCapture(video_path)
    
    for frame_id in [30, 40]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Test with very low threshold to catch any hint of squirrel
        for threshold in [0.3, 0.1, 0.05, 0.01]:
            for cls_list in [
                ['squirrel', 'bird'],
                ['chipmunk', 'bird'],
                ['squirrel', 'chipmunk', 'bird', 'sparrow'],
            ]:
                model.set_classes(cls_list)
                results = model.predict(frame, verbose=False, conf=threshold)[0]
                boxes = results.boxes
                dets = []
                for box in boxes:
                    name = model.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    if name != 'bird':  # highlight non-bird detections
                        dets.append(f">>{name}:{conf:.2f}<<")
                    else:
                        dets.append(f"{name}:{conf:.2f}")
                non_bird = [d for d in dets if '>>' in d]
                if non_bird:
                    print(f"  F{frame_id} t={threshold:.2f} {str(cls_list[:3]):30s} => NON-BIRD: {', '.join(non_bird)}", flush=True)
    
    cap.release()

print("\nDone.", flush=True)
