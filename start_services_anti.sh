#!/bin/bash
source /home/rayu/DasTern/.venv/bin/activate
export OCR_SERVICE_HOST=0.0.0.0
export OCR_SERVICE_PORT=8000
export AI_SERVICE_HOST=0.0.0.0
export AI_SERVICE_PORT=8001
export OLLAMA_MODEL=llama3.2:3b

# Start OCR Service
echo "Starting OCR Service..."
python /home/rayu/DasTern/ocr-service-anti/main.py 8000 > ocr_service_run.log 2>&1 &
OCR_PID=$!
echo "Started OCR Service (PID: $OCR_PID)"

# Start AI Service
echo "Starting AI Service..."
# Use python -m to run the module so imports work correctly
cd /home/rayu/DasTern/ai-llm-service
python -m app.main > ai_service_run.log 2>&1 &
AI_PID=$!
echo "Started AI Service (PID: $AI_PID)"

echo "Services are running in background."
