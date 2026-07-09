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
        self.is_live_camera = isinstance(video_source, int) or (
            isinstance(video_source, str) and video_source.isdigit())

        # Open video capture — try multiple backends for best compatibility
        if self.is_live_camera:
            cam_idx = int(video_source) if isinstance(video_source, str) else video_source
            # Try default first (best for virtual cameras like Camo Studio, OBS)
            self.cap = cv2.VideoCapture(cam_idx)
            if not self.cap.isOpened():
                # Fallback: DSHOW (good for physical USB webcams)
                self.logger.info(f"Default backend failed, trying DSHOW...")
                self.cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                # Last resort: MSMF
                self.logger.info(f"DSHOW failed, trying MSMF...")
                self.cap = cv2.VideoCapture(cam_idx, cv2.CAP_MSMF)
        else:
            self.cap = cv2.VideoCapture(video_source)

        if not self.cap.isOpened():
            self.logger.error(f"Failed to open video source: {video_source}")
            raise ValueError(f"Could not open video source: {video_source}")

        self.logger.info(f"Video source opened: {video_source}")

    def process(self, callback=None, max_frames=None, live_preview=True):
        """
        Read frames, run detection, and invoke callback for each frame.

        Args:
            callback: function(frame, detections, frame_result) called per frame
            max_frames: max number of frames to process (None = continuous)
            live_preview: show frames in a window using cv2.imshow (default True for webcams)
        """
        frame_count = 0
        self.logger.info("Starting video processing loop...")
        if self.is_live_camera:
            self.logger.info("📱 Live camera mode — press 'q' to quit | 'p' to pause/resume")

        paused = False

        while True:
            if max_frames is not None and frame_count >= max_frames:
                self.logger.info(f"Reached max_frames limit ({max_frames})")
                break

            if not paused:
                ret, frame = self.cap.read()
                if not ret:
                    if self.is_live_camera:
                        self.logger.warning("Frame capture failed, retrying...")
                        continue
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

            # --- Live preview window ---
            if live_preview and 'annotated' in dir():
                pass  # annotated frame managed by callback

            # Keyboard controls (only in live mode)
            if self.is_live_camera or live_preview:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("User pressed 'q' — stopping...")
                    break
                elif key == ord('p'):
                    paused = not paused
                    status = "PAUSED" if paused else "RESUMED"
                    self.logger.info(f"⏸️  {status}")
                    cv2.putText(frame, status, (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                    cv2.imshow('AI Video Detection — Live', frame)
                    cv2.waitKey(500)

        self.logger.info(f"Processed {frame_count} frames total")
        self.release()
        if live_preview:
            cv2.destroyAllWindows()

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
