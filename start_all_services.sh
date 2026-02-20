#!/bin/bash
# Start all backend services for DasTern OCR Flutter App
# This script starts both OCR and AI services in the background

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/macbook/CADT/DasTern"

echo -e "${GREEN}🚀 Starting DasTern Backend Services${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Ollama is running
echo -e "${YELLOW}Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ ERROR: Ollama is NOT running!${NC}"
    echo "   Start Ollama first, then run this script again"
    echo "   Run: ollama serve"
    exit 1
fi

# Start OCR Service in background
echo ""
echo -e "${YELLOW}Starting OCR Service (port 8000)...${NC}"
cd "$PROJECT_ROOT/ocr-service-anti"
source venv/bin/activate && python main.py 8000 > /tmp/ocr_service.log 2>&1 &
OCR_PID=$!
echo -e "${GREEN}✅ OCR Service started (PID: $OCR_PID)${NC}"

# Start AI Service in background
echo ""
echo -e "${YELLOW}Starting AI Service (port 8001)...${NC}"
cd "$PROJECT_ROOT/ai-llm-service"
source venv/bin/activate && python app/main_ollama.py > /tmp/ai_service.log 2>&1 &
AI_PID=$!
echo -e "${GREEN}✅ AI Service started (PID: $AI_PID)${NC}"

# Wait for services to be ready
echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 2

# Test connections
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Testing Service Health...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test OCR Service
if curl -s http://127.0.0.1:8000/health | grep -q '"status"'; then
    echo -e "${GREEN}✅ OCR Service is healthy (http://127.0.0.1:8000)${NC}"
else
    echo -e "${RED}⚠️  OCR Service health check inconclusive${NC}"
fi

# Test AI Service
if curl -s http://127.0.0.1:8001/health | grep -q '"status"'; then
    echo -e "${GREEN}✅ AI Service is healthy (http://127.0.0.1:8001)${NC}"
else
    echo -e "${RED}⚠️  AI Service health check inconclusive${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Service URLs:"
echo "   • OCR Service:  http://127.0.0.1:8000"
echo "   • AI Service:   http://127.0.0.1:8001"
echo "   • Ollama:       http://localhost:11434"
echo ""
echo "📝 Logs:"
echo "   • OCR Service: tail -f /tmp/ocr_service.log"
echo "   • AI Service:  tail -f /tmp/ai_service.log"
echo ""
echo "⚠️  To stop services, run: kill $OCR_PID $AI_PID"
echo ""
echo "✅ Flutter app can now connect to the services!"
