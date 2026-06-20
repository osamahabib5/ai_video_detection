#!/bin/bash
# Activate venv and run the application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "🚀 AI Video Detection System"
echo "============================"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found. Running setup first..."
    bash "$SCRIPT_DIR/setup.sh"
fi

# Detect activation path (Windows=Scripts/, Unix=bin/)
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    VENV_ACTIVATE="$VENV_DIR/Scripts/activate"
elif [ -f "$VENV_DIR/bin/activate" ]; then
    VENV_ACTIVATE="$VENV_DIR/bin/activate"
else
    echo "❌ Cannot find venv activation script!"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_ACTIVATE"

echo "✓ Environment activated"
echo ""

# Run the application
echo "🎯 Starting video detection..."
python -m app.main "$@"
