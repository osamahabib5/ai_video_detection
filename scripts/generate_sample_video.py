#!/usr/bin/env python3
"""
Generate sample video for testing
"""
import cv2
import numpy as np
from pathlib import Path


def create_sample_video(output_path='data/videos/sample.mp4', duration_seconds=5):
    """Create a sample video with moving rectangles"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    width, height = 1280, 720
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    total_frames = int(fps * duration_seconds)
    
    print(f"Creating sample video: {output_path}")
    
    for frame_num in range(total_frames):
        frame = np.ones((height, width, 3), dtype=np.uint8) * 200
        
        # Draw moving rectangles
        x = int((frame_num / total_frames) * (width - 200))
        y = int((height - 200) / 2)
        
        cv2.rectangle(frame, (x, y), (x + 200, y + 200), (0, 255, 0), -1)
        cv2.rectangle(frame, (x + 100, y + 50), (x + 300, y + 150), (255, 0, 0), -1)
        
        # Add frame counter
        cv2.putText(
            frame, f"Frame: {frame_num + 1}/{total_frames}",
            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
        )
        
        out.write(frame)
        
        if (frame_num + 1) % 30 == 0:
            print(f"  Progress: {frame_num + 1}/{total_frames} frames")
    
    out.release()
    print(f"✓ Sample video created: {output_path}")


if __name__ == '__main__':
    create_sample_video()
