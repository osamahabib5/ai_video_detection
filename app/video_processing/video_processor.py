import cv2
import logging
from pathlib import Path

class VideoProcessor:
    def __init__(self, source, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.source = source
        
        # Check if source is a Web URL (direct HTTP/HTTPS)
        if isinstance(source, str) and (source.startswith('http://') or source.startswith('https://')):
            self.logger.info(f"Using direct web URL: {source}")

        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            self.logger.error(f"Failed to open video source: {source}")
            raise ValueError(f"Could not open video source: {source}")

    

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()

    @property
    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS) or 30

    @property
    def frame_size(self):
        return (
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )

class VideoWriter:
    def __init__(self, output_path: str, fps: float = 30, frame_size: tuple = (1280, 720)):
        self.logger = logging.getLogger(__name__)
        self.output_path = output_path
        
        # Using XVID and .avi for maximum compatibility across Windows/Linux
        # Ensure the output filename in config ends in .avi
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        
        if not self.writer.isOpened():
            self.logger.error(f"Failed to initialize VideoWriter at {output_path}")
        else:
            self.logger.info(f"VideoWriter initialized: {output_path} ({fps} FPS)")

    def write(self, frame):
        if self.writer:
            self.writer.write(frame)

    def release(self):
        if self.writer:
            self.writer.release()
            self.logger.info("VideoWriter released.")