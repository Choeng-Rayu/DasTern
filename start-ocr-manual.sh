#!/bin/bash
# Start OCR Service Manually with PaddleOCR (Python 3.11 venv)

echo "Starting OCR Service with PaddleOCR on port 8000..."
cd /home/rayu/DasTern/ocr-service

# CRITICAL: Set Paddle environment variables FIRST (before venv activation)
# This ensures they're set at the process level before any Python code runs
export PADDLE_WITH_ONEDNN=0
export FLAGS_use_mkldnn=0
export PADDLE_MKLDNN_FALLBACK_ON_MISMATCH=1
export PADDLE_INFERENCE_DISABLE_ONEDNN=1

# Use Python 3.11 venv with PaddleOCR instead of main .venv
source /home/rayu/DasTern/ocr-service/venv_ocr/bin/activate

# Set environment variables
export AI_LLM_SERVICE_URL="http://localhost:8001"
export PYTHONPATH=/home/rayu/DasTern/ocr-service:$PYTHONPATH

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
