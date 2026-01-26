#!/bin/bash

# Start all DasTern services

echo "🚀 Starting DasTern services..."

cd /home/rayu/DasTern

# Activate Python virtual environment
source .venv/bin/activate

# Start Ollama
echo "Starting Ollama..."
nohup ollama serve > ollama.log 2>&1 &
sleep 2

# Start OCR Service
echo "Starting OCR service on port 8004..."
cd ocr-service
nohup uvicorn app.main:app --reload --port 8004 --host 0.0.0.0 > ocr.log 2>&1 &
cd ..

# Start AI Service
echo "Starting AI service on port 8005..."
cd ai-llm-service
nohup uvicorn app.main:app --reload --port 8005 --host 0.0.0.0 > ai.log 2>&1 &
cd ..

# Start Backend
echo "Starting Backend on port 3000..."
cd backend-nextjs
nohup npm run dev > backend.log 2>&1 &
cd ..

echo "⏳ Waiting for services to start..."
sleep 5

echo "✅ All services started!"
echo
./check-services.sh
