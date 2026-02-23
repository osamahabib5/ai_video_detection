# Makefile for AI Video Detection System

.PHONY: help build run stop logs test clean

help:
	@echo "AI Video Detection System - Available Commands"
	@echo ""
	@echo "  make build         - Build Docker image"
	@echo "  make run           - Run container with docker-compose"
	@echo "  make stop          - Stop running containers"
	@echo "  make logs          - View container logs"
	@echo "  make logs-follow   - Follow container logs"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up Docker resources"
	@echo "  make shell         - Open shell in container"
	@echo "  make download-models - Download YOLO models"
	@echo "  make generate-sample - Generate sample video"

build:
	@echo "Building Docker image..."
	docker build -t ai-video-detection:latest .
	@echo "✓ Build complete"

run:
	@echo "Starting container..."
	docker-compose up -d
	@echo "✓ Container started"

stop:
	@echo "Stopping container..."
	docker-compose down
	@echo "✓ Container stopped"

logs:
	docker-compose logs video-detection

logs-follow:
	docker-compose logs -f video-detection

test:
	docker-compose exec video-detection pytest tests/

clean:
	@echo "Cleaning up..."
	docker-compose down
	docker rmi ai-video-detection:latest 2>/dev/null || true
	docker builder prune -f
	@echo "✓ Cleanup complete"

shell:
	docker-compose exec video-detection /bin/bash

download-models:
	docker-compose exec video-detection python -m scripts.download_models

generate-sample:
	docker-compose exec video-detection python -m scripts.generate_sample_video

run-detection:
	docker-compose exec video-detection python -m app.main

.DEFAULT_GOAL := help
