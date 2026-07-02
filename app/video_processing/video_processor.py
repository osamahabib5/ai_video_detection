import cv2
import logging
import time
from pathlib import Path


class VideoProcessor:
    """Orchestrates video capture, detection, and frame processing."""

    def __init__(self, detector, video_source, config=None):
        self.logger = logging.getLogger(__name__)
        self.detector = detector
        self.config = config

        # Normalize source: Path objects -> string
        if isinstance(video_source, Path):
            video_source = str(video_source)

        # Handle HTTP/HTTPS URLs
        if isinstance(video_source, str) and (video_source.startswith('http://') or video_source.startswith('https://')):
            self.logger.info(f"Using direct web URL: {video_source}")

        self.source = video_source

        # Open video capture
        self.cap = cv2.VideoCapture(video_source)

        if not self.cap.isOpened():
            self.logger.error(f"Failed to open video source: {video_source}")
            raise ValueError(f"Could not open video source: {video_source}")

        self.logger.info(f"Video source opened: {video_source}")

    def process(self, callback=None, max_frames=None):
        """
        Read frames, run detection, and invoke callback for each frame.

        Args:
            callback: function(frame, detections, frame_result) called per frame
            max_frames: max number of frames to process (None = all)
        """
        frame_count = 0
        self.logger.info("Starting video processing loop...")

        while True:
            if max_frames is not None and frame_count >= max_frames:
                self.logger.info(f"Reached max_frames limit ({max_frames})")
                break

            ret, frame = self.cap.read()
            if not ret:
                self.logger.info("End of video stream reached")
                break

            # Run detection on this frame
            t_start = time.time()
            detections, inference_time = self.detector.predict(frame)
            total_time = time.time() - t_start

            # Build frame result
            frame_result = {
                'frame_id': frame_count,
                'inference_time': inference_time,
                'total_processing_time': total_time,
            }

            # Invoke callback if provided
            if callback:
                callback(frame, detections, frame_result)

            frame_count += 1

        self.logger.info(f"Processed {frame_count} frames total")
        self.release()

    def release(self):
        """Release video capture resources."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.logger.info("Video capture released")


class VideoWriter:
    """Writes annotated frames to an output video file."""

    def __init__(self, output_path: str, fps: float = 30, frame_size: tuple = (1280, 720)):
        self.logger = logging.getLogger(__name__)
        self.output_path = output_path

        # Using XVID and .avi for maximum compatibility across Windows/Linux
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

        if not self.writer.isOpened():
            self.logger.error(f"Failed to initialize VideoWriter at {output_path}")
        else:
            self.logger.info(f"VideoWriter initialized: {output_path} ({fps} FPS)")

    def write_frame(self, frame):
        """Write a single frame to the output video."""
        if self.writer:
            self.writer.write(frame)

    def release(self):
        """Release video writer resources."""
        if self.writer:
            self.writer.release()
            self.logger.info("VideoWriter released")
