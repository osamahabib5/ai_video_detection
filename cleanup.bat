@echo off
REM Clean up Docker resources on Windows

setlocal enabledelayedexpansion

echo 🧹 Stopping containers...
docker-compose down

echo 🗑️  Removing images...
docker rmi ai-video-detection:latest 2>nul
docker rmi ai-video-detection:gpu 2>nul

echo 🗑️  Pruning build cache...
docker builder prune -f

echo ✓ Cleanup complete!

endlocal
