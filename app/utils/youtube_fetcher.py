"""
YouTube Video Fetcher
=====================
Downloads or streams YouTube videos into the video processing pipeline.
Uses yt-dlp (maintained fork of youtube-dl) for reliable extraction.
"""
import logging
import subprocess
import tempfile
from pathlib import Path


class YouTubeFetcher:
    """Handles YouTube video downloading for the detection pipeline."""

    def __init__(self, output_dir=None):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / 'ai_video_detection'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_youtube_url(self, url):
        """Check if a URL is a YouTube video."""
        if not isinstance(url, str):
            return False
        return any(domain in url.lower() for domain in (
            'youtube.com/watch', 'youtu.be/', 'youtube.com/shorts/'))

    def fetch(self, url, quality='best[height<=720]', timeout=120):
        """
        Download a YouTube video and return the local file path.

        Args:
            url: YouTube video URL
            quality: yt-dlp format selector (default: 720p max for reasonable size)
            timeout: download timeout in seconds

        Returns:
            Path to the downloaded video file, or None on failure.
        """
        if not self.is_youtube_url(url):
            return None

        self.logger.info(f"Fetching YouTube video: {url}")

        # Extract video ID for filename
        video_id = self._extract_video_id(url)
        output_template = str(self.output_dir / f'{video_id}.mp4')

        # Skip if already downloaded
        if Path(output_template).exists():
            self.logger.info(f"Video already cached: {output_template}")
            return output_template

        # Build yt-dlp command
        cmd = [
            'yt-dlp',
            '-f', quality,
            '-o', output_template,
            '--no-playlist',
            '--merge-output-format', 'mp4',
            '--socket-timeout', str(timeout),
            url,
        ]

        try:
            self.logger.info(f"Downloading with yt-dlp...")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout + 30
            )
            if result.returncode != 0:
                # Try fallback: best available
                self.logger.warning(f"First attempt failed, trying best available quality...")
                cmd[2] = 'best'
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout + 30
                )

            if result.returncode == 0 and Path(output_template).exists():
                file_size_mb = Path(output_template).stat().st_size / (1024 * 1024)
                self.logger.info(f"Downloaded: {output_template} ({file_size_mb:.1f} MB)")
                return output_template
            else:
                self.logger.error(f"yt-dlp failed: {result.stderr[:300]}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("YouTube download timed out")
            return None
        except FileNotFoundError:
            self.logger.error(
                "yt-dlp not found. Install with: pip install yt-dlp"
            )
            return None
        except Exception as e:
            self.logger.error(f"YouTube download error: {e}")
            return None

    def get_stream_url(self, url, quality='best[height<=720]'):
        """
        Get a direct streamable URL (useful for live processing without full download).

        Returns:
            Direct video URL string, or None.
        """
        if not self.is_youtube_url(url):
            return None

        cmd = [
            'yt-dlp', '-f', quality, '-g', '--no-playlist', url
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                stream_url = result.stdout.strip().split('\n')[0]
                self.logger.info(f"Got stream URL (first 60 chars): {stream_url[:60]}...")
                return stream_url
        except Exception as e:
            self.logger.error(f"Stream URL extraction failed: {e}")
        return None

    def _extract_video_id(self, url):
        """Extract YouTube video ID from URL."""
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        # Fallback: hash the URL
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:12]
