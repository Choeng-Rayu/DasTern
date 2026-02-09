#!/bin/bash
# Start all DasTern services with optimized settings

echo "🚀 Starting DasTern Services..."
echo "================================"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama not running. Starting Ollama..."
    ollama serve &
    sleep 3
else
    echo "✅ Ollama already running"
fi

# Kill existing service processes
echo "🔄 Stopping existing services..."
pkill -f "python.*main_ollama.py" 2>/dev/null || true
pkill -f "python.*main.py.*ocr" 2>/dev/null || true
sleep 2

# Start OCR Service
echo "📷 Starting OCR Service (port 8000)..."
cd /home/rayu/DasTern/ocr-service-anti
python main.py > /tmp/ocr_service.log 2>&1 &
OCR_PID=$!
echo "   PID: $OCR_PID"

# Start AI-LLM Service with OPTIMIZED TIMEOUT
echo "🤖 Starting AI-LLM Service (port 8001) with 10-minute timeout..."
cd /home/rayu/DasTern/ai-llm-service
export OLLAMA_TIMEOUT=600  # 10 minutes for complex prescriptions
export MODEL=llama3.2:3b   # Fast model
python app/main_ollama.py > /tmp/ai_service.log 2>&1 &
AI_PID=$!
echo "   PID: $AI_PID"
echo "   OLLAMA_TIMEOUT=$OLLAMA_TIMEOUT"

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service health
echo ""
echo "🔍 Checking service health..."

# Check OCR Service
if curl -s http://localhost:8000/ | grep -q "OCR Service"; then
    echo "✅ OCR Service: Running"
else
    echo "❌ OCR Service: Failed to start"
fi

# Check AI Service
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ AI Service: Running"
    curl -s http://localhost:8001/health | jq -r '. | "   Status: \(.status), Ollama: \(.ollama_connected)"'
else
    echo "❌ AI Service: Failed to start"
fi

echo ""
echo "================================"
echo "✅ Services started!"
echo ""
echo "📝 Logs:"
echo "   OCR Service:  tail -f /tmp/ocr_service.log"
echo "   AI Service:   tail -f /tmp/ai_service.log"
echo ""
echo "🛑 To stop services:"
echo "   kill $OCR_PID $AI_PID"
echo "   # or"
echo "   pkill -f 'python.*main'"
echo ""
echo "🧪 To test:"
echo "   cd /home/rayu/DasTern/ocr_ai_for_reminder"
echo "   flutter run -d linux"
