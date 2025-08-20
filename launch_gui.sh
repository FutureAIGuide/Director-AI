#!/bin/bash

# URL Screenshot Processor GUI Launcher
# This script launches the GUI with proper environment setup

echo "🚀 Launching URL Screenshot Processor GUI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_and_run.sh first."
    exit 1
fi

# Activate virtual environment and get Python path
source venv/bin/activate
PYTHON_EXE=$(which python)

# Check if GUI script exists
if [ ! -f "gui_screenshot_processor.py" ]; then
    echo "❌ GUI script not found. Please ensure gui_screenshot_processor.py is in this directory."
    exit 1
fi

# Launch GUI with correct Python executable
echo "✅ Starting GUI application..."
echo "🐍 Using Python: $PYTHON_EXE"
$PYTHON_EXE gui_screenshot_processor.py

echo "📱 GUI application closed."
