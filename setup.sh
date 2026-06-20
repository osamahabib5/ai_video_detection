#!/bin/bash
# Setup Python virtual environment and install dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "🐍 Setting up Python Virtual Environment..."
echo "============================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment at: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists at: $VENV_DIR"
fi

# Activate and install dependencies
echo ""
echo "📦 Activating environment and installing dependencies..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install PyTorch (CPU version by default)
echo ""
echo "🔥 Installing PyTorch (CPU version)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
echo ""
echo "📚 Installing project dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p "$SCRIPT_DIR/data/models"
mkdir -p "$SCRIPT_DIR/data/videos"
mkdir -p "$SCRIPT_DIR/logs/predictions"

echo ""
echo "============================================"
echo "✅ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python -m app.main"
echo ""
echo "To start the API server:"
echo "  uvicorn app.api:app --host 0.0.0.0 --port 8000"
echo ""
