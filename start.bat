@echo off
REM Build and run the Docker container on Windows

setlocal enabledelayedexpansion

echo 🔨 Building Docker image...
docker build -t ai-video-detection:latest .

if !errorlevel! neq 0 (
    echo ✗ Build failed!
    exit /b 1
)

echo 📦 Image built successfully!

echo 🚀 Starting container with docker-compose...
docker-compose up -d

echo ✓ Container started!
echo.
echo Available services:
echo   - Video Detection: localhost:8000
echo.
echo View logs:
echo   docker-compose logs -f video-detection
echo.
echo Stop container:
echo   docker-compose down

endlocal
