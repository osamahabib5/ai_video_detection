#!/bin/bash
# Setup Python virtual environment and install dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "🐍 Setting up Python Virtual Environment..."
echo "============================================"

# Check Python version (try python3 first, fall back to python on Windows)
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment at: $VENV_DIR"
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists at: $VENV_DIR"
fi

# Detect Windows vs Unix activate path
# On Windows (even Git Bash), Python venv uses Scripts/ not bin/
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    VENV_ACTIVATE="$VENV_DIR/Scripts/activate"
    echo "🪟 Detected Windows-style venv (Scripts/)"
elif [ -f "$VENV_DIR/bin/activate" ]; then
    VENV_ACTIVATE="$VENV_DIR/bin/activate"
    echo "🐧 Detected Unix-style venv (bin/)"
else
    echo "❌ Cannot find venv activation script!"
    exit 1
fi

# Activate and install dependencies
echo ""
echo "📦 Activating environment and installing dependencies..."
source "$VENV_ACTIVATE"

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
echo "To activate the environment later, run:"
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    echo "  source venv/Scripts/activate"
else
    echo "  source venv/bin/activate"
fi
echo ""
echo "To run the application:"
echo "  python -m app.main"
echo ""
echo "To start the API server:"
echo "  uvicorn app.api:app --host 0.0.0.0 --port 8000"
echo ""
