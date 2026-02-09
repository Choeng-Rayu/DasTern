#!/bin/bash
# Enable immediate exit on error
set -e

# Activate virtual environment
source /home/rayu/DasTern/.venv/bin/activate

# Set environment variables
export OCR_SERVICE_HOST=0.0.0.0
export OCR_SERVICE_PORT=8000
export AI_SERVICE_URL="http://localhost:8001"
export LOG_LEVEL=INFO

echo "🚀 Starting OCR Service (Foreground)..."
echo "logs will appear below:"
echo "-----------------------------------"

# Run Python script directly
python /home/rayu/DasTern/ocr-service-anti/main.py 8000
