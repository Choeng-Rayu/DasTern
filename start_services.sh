#!/bin/bash
# Complete Setup and Run Guide for OCR + AI Pipeline
# This script helps you start both services and run tests

echo "=========================================="
echo "🚀 DasTern OCR + AI Pipeline Setup"
echo "=========================================="
echo ""

# Function to check if a port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
    return $?
}

# Function to check if a service is responding
check_service() {
    curl -s $1/health > /dev/null 2>&1
    return $?
}

echo "📋 Step 1: Checking current status..."
echo "------------------------------------------"

# Check OCR Service
if check_service "http://localhost:8000"; then
    echo "✅ OCR Service: Already running on port 8000"
    OCR_RUNNING=true
else
    echo "❌ OCR Service: Not running on port 8000"
    OCR_RUNNING=false
fi

# Check AI Service  
if check_service "http://localhost:8001"; then
    echo "✅ AI Service: Already running on port 8001"
    AI_RUNNING=true
else
    echo "❌ AI Service: Not running on port 8001"
    AI_RUNNING=false
fi

echo ""
echo "📋 Step 2: Starting services..."
echo "------------------------------------------"

# Start OCR Service if not running
if [ "$OCR_RUNNING" = false ]; then
    echo "🚀 Starting OCR Service on port 8000..."
    cd /home/rayu/DasTern/ocr-service
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Start in background
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/ocr_service.log 2>&1 &
    OCR_PID=$!
    echo "   PID: $OCR_PID"
    echo "   Log: /tmp/ocr_service.log"
    
    # Wait for it to start
    echo "   Waiting for OCR service to start..."
    for i in {1..30}; do
        if check_service "http://localhost:8000"; then
            echo "   ✅ OCR Service is ready!"
            break
        fi
        sleep 1
        echo "   ... ($i/30)"
    done
    
    if ! check_service "http://localhost:8000"; then
        echo "   ❌ OCR Service failed to start. Check log: /tmp/ocr_service.log"
    fi
else
    echo "✅ OCR Service already running"
fi

echo ""

# Start AI Service if not running
if [ "$AI_RUNNING" = false ]; then
    echo "🚀 Starting AI Service on port 8001..."
    cd /home/rayu/DasTern/ai-llm-service
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Set environment variables
    export OLLAMA_BASE_URL=http://localhost:11434
    export OLLAMA_MODEL=llama3.2:3b
    
    # Start in background
    python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001 > /tmp/ai_service.log 2>&1 &
    AI_PID=$!
    echo "   PID: $AI_PID"
    echo "   Log: /tmp/ai_service.log"
    
    # Wait for it to start
    echo "   Waiting for AI service to start..."
    for i in {1..30}; do
        if check_service "http://localhost:8001"; then
            echo "   ✅ AI Service is ready!"
            break
        fi
        sleep 1
        echo "   ... ($i/30)"
    done
    
    if ! check_service "http://localhost:8001"; then
        echo "   ❌ AI Service failed to start. Check log: /tmp/ai_service.log"
    fi
else
    echo "✅ AI Service already running"
fi

echo ""
echo "=========================================="
echo "✅ Services Status"
echo "=========================================="

# Final check
if check_service "http://localhost:8000"; then
    echo "✅ OCR Service: http://localhost:8000"
    OCR_READY=true
else
    echo "❌ OCR Service: Not ready"
    OCR_READY=false
fi

if check_service "http://localhost:8001"; then
    echo "✅ AI Service: http://localhost:8001"
    AI_READY=true
else
    echo "❌ AI Service: Not ready"
    AI_READY=false
fi

if [ "$OCR_READY" = true ] && [ "$AI_READY" = true ]; then
    echo ""
    echo "🎉 Both services are running!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run the pipeline test:"
    echo "      cd /home/rayu/DasTern/OCR_Test_Space"
    echo "      python3 test_full_pipeline.py"
    echo ""
    echo "   2. Or use the helper script:"
    echo "      ./run_pipeline_test.sh"
    echo ""
    echo "⏱️  Note: Each image takes 40-120 seconds to process"
    echo "   (OCR is fast, AI is slow on CPU)"
else
    echo ""
    echo "❌ Some services failed to start. Check the logs:"
    echo "   OCR: /tmp/ocr_service.log"
    echo "   AI: /tmp/ai_service.log"
fi
