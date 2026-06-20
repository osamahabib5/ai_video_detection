#!/bin/bash
# Clean up virtual environment and cached files

echo "🧹 Cleaning up project..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Remove virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "🗑️  Removing virtual environment..."
    rm -rf "$SCRIPT_DIR/venv"
fi

# Remove Python cache files
echo "🗑️  Removing Python cache..."
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove pytest cache
echo "🗑️  Removing test cache..."
rm -rf "$SCRIPT_DIR/.pytest_cache" 2>/dev/null || true

# Optional: remove logs and models (uncomment if needed)
# rm -rf "$SCRIPT_DIR/logs" 2>/dev/null || true
# rm -rf "$SCRIPT_DIR/data/models" 2>/dev/null || true

echo "✓ Cleanup complete!"
echo ""
echo "To rebuild from scratch:"
echo "  bash setup.sh"
