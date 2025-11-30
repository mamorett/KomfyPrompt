#!/bin/bash
# Launch script for ComfyUI Prompt Extractor

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if required packages are installed
python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: PyQt6 is not installed"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi

# Run the application
python3 main.py