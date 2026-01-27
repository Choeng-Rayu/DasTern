#!/bin/bash
# OCR Service Startup Script (Port 8001)
# Uses port 8001 if port 8000 is busy

# Kill any existing uvicorn processes
pkill -f "uvicorn.*ocr" || true
sleep 1

# Set Paddle environment variables to try disabling oneDNN
# Note: These don't always work due to shared library loading timing
export PADDLE_WITH_ONEDNN=0
export FLAGS_use_mkldnn=0
export PADDLE_MKLDNN_FALLBACK_ON_MISMATCH=1
export DISABLE_MODEL_SOURCE_CHECK=True

# Create a Python wrapper to start the service
# This approach starts uvicorn directly without shell expansion issues
source /home/rayu/DasTern/ocr-service/venv_ocr/bin/activate

cd /home/rayu/DasTern/ocr-service

echo "=========================================="
echo "Starting OCR Service"
echo "Port: 8001"
echo "Environment: Python 3.11 with PaddleOCR 3.3.3"
echo "=========================================="

# Try to start on port 8001
exec uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
