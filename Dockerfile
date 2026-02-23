# Use official Python runtime as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TORCH_HOME=/tmp/torch_models \
    YOLO_HOME=/tmp/yolo_models

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     # Add these two lines specifically:
#     libgl1 \
#     libglib2.0-0 \
#     # Keep your existing ones:
#     libsm6 \
#     libxext6 \
#     libxrender-dev \
#     libgomp1 \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy requirements first for better caching
# COPY requirements.txt .

# # Install Python dependencies
# # RUN pip install --no-cache-dir -r requirements.txt

# # Change your pip install line to this:
# RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
#     pip install --no-cache-dir -r requirements.txt


# ... (Base image and ENV lines remain the same)

# 1. Ensure system libraries are present
RUN apt-get update && apt-get install -y \
    build-essential curl libgl1 libglib2.0-0 \
    libsm6 libxext6 libxrender-dev libgomp1 git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# 2. Install CPU-ONLY Torch first, then the rest
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# ... (Rest of the COPY and ENTRYPOINT lines remain the same)

# Copy application code
COPY app/ app/
COPY data/ data/
COPY logs/ logs/

# Create necessary directories
RUN mkdir -p logs/predictions && \
    mkdir -p data/models && \
    mkdir -p data/videos

# Expose port for API (if applicable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from app.detectors.yolo_detector import ObjectDetector; ObjectDetector()" || exit 1

# Set entrypoint
ENTRYPOINT ["python", "-m", "app.main"]
