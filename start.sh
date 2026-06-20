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

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "✓ Environment activated"
echo ""

# Run the application
echo "🎯 Starting video detection..."
python -m app.main "$@"
