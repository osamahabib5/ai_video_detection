# Makefile for AI Video Detection System (venv-based)

.PHONY: help setup start stop clean test shell

VENV_DIR := venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

# Detect OS (Windows vs Unix)
ifeq ($(OS),Windows_NT)
	VENV_ACTIVATE := $(VENV_DIR)/Scripts/activate
	VENV_PYTHON := $(VENV_DIR)/Scripts/python
	VENV_PIP := $(VENV_DIR)/Scripts/pip
	RM := rmdir /s /q
else
	VENV_ACTIVATE := source $(VENV_DIR)/bin/activate
	RM := rm -rf
endif

help:
	@echo "AI Video Detection System - Available Commands"
	@echo ""
	@echo "  make setup          - Create venv and install dependencies"
	@echo "  make run            - Run video detection"
	@echo "  make api            - Start FastAPI server on port 8000"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Remove venv and cached files"
	@echo "  make shell          - Activate venv shell"
	@echo "  make download-models - Download YOLO models"
	@echo "  make generate-sample - Generate sample video"
	@echo "  make logs           - View application logs"

setup: $(VENV_DIR)/pyvenv.cfg

$(VENV_DIR)/pyvenv.cfg:
	@echo "🔧 Creating Python virtual environment..."
	python3 -m venv $(VENV_DIR) || python -m venv $(VENV_DIR)
	@echo "⬆️  Upgrading pip..."
	$(VENV_PIP) install --upgrade pip
	@echo "🔥 Installing PyTorch (CPU)..."
	$(VENV_PIP) install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
	@echo "📚 Installing dependencies..."
	$(VENV_PIP) install -r requirements.txt
	@echo "📁 Creating directories..."
	mkdir -p data/models data/videos logs/predictions
	@echo "✓ Setup complete"

run:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "⚠️  venv not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🎯 Starting video detection..."
	$(VENV_PYTHON) -m app.main $(ARGS)

api:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "⚠️  venv not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🌐 Starting API server on http://localhost:8000..."
	$(VENV_PYTHON) -m uvicorn app.api:app --host 0.0.0.0 --port 8000

test:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "⚠️  venv not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m pytest tests/

clean:
	@echo "🧹 Cleaning up..."
	-$(RM) $(VENV_DIR) 2>/dev/null || true
	-find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	-find . -type f -name "*.pyc" -delete 2>/dev/null || true
	-rm -rf .pytest_cache 2>/dev/null || true
	@echo "✓ Cleanup complete"

shell:
	@echo "🔌 Activating virtual environment shell..."
	@echo "Run 'deactivate' to exit the venv."
	@bash --init-file <(echo '. "$(VENV_DIR)/bin/activate"')

download-models:
	$(VENV_PYTHON) -m scripts.download_models

generate-sample:
	$(VENV_PYTHON) -m scripts.generate_sample_video

logs:
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "No log file found. Run the application first."; \
	fi

.DEFAULT_GOAL := help
