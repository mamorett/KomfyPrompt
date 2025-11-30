#!/bin/bash
# Installation script for ComfyUI Prompt Extractor

echo "Installing ComfyUI Prompt Extractor dependencies..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

# Install required packages
echo "Installing required Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation completed successfully!"
    echo ""
    echo "To run the application:"
    echo "  ./run.sh"
    echo "  or"
    echo "  python3 main.py"
    echo ""
    echo "Optional: For translation support, install:"
    echo "  pip3 install translators"
else
    echo ""
    echo "✗ Installation failed. Please check the error messages above."
    exit 1
fi