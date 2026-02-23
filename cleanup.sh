#!/bin/bash
# Clean up Docker resources

echo "🧹 Stopping containers..."
docker-compose down

echo "🗑️  Removing images..."
docker rmi ai-video-detection:latest 2>/dev/null || true
docker rmi ai-video-detection:gpu 2>/dev/null || true

echo "🗑️  Removing build cache..."
docker builder prune -f

echo "✓ Cleanup complete!"
