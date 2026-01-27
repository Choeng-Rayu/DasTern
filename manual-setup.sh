#!/bin/bash
# Complete Manual Startup Script for DasTern OCR Testing

echo "=================================="
echo "DasTern Manual Testing Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .venv exists
if [ ! -d "/home/rayu/DasTern/.venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at /home/rayu/DasTern/.venv${NC}"
    exit 1
fi

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    ollama serve &
    sleep 3
fi

# Check if llama3.1:8b model is available
if ! ollama list | grep -q "llama3.1:8b"; then
    echo -e "${YELLOW}Model llama3.1:8b not found. Pulling model (this may take a while)...${NC}"
    ollama pull llama3.1:8b
fi

echo -e "${GREEN}✓ Ollama ready${NC}"
echo ""

# Create test images directory if it doesn't exist
mkdir -p /home/rayu/DasTern/test_images

echo "=================================="
echo "Starting Services"
echo "=================================="
echo ""

# Function to start service in new terminal or background
start_service() {
    local name=$1
    local port=$2
    local script=$3
    
    echo -e "${YELLOW}Starting $name on port $port...${NC}"
    echo "  Command: $script"
    echo "  Access at: http://localhost:$port"
    echo ""
}

echo -e "${GREEN}To start the services, open 3 separate terminals and run:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 - OCR Service:${NC}"
echo "  cd /home/rayu/DasTern && ./start-ocr-manual.sh"
echo ""
echo -e "${YELLOW}Terminal 2 - AI LLM Service:${NC}"
echo "  cd /home/rayu/DasTern && ./start-ai-llm-manual.sh"
echo ""
echo -e "${YELLOW}Terminal 3 - Test Interface:${NC}"
echo "  cd /home/rayu/DasTern/ai_ocr_interface_test && npm run dev"
echo ""

echo "=================================="
echo "Testing"
echo "=================================="
echo ""
echo "Once all services are running:"
echo "1. Open http://localhost:3000/test-ocr in your browser"
echo "2. Upload a prescription image"
echo "3. Click 'Process with OCR'"
echo "4. Check the accuracy of extracted text"
echo ""
echo -e "${GREEN}Service URLs:${NC}"
echo "  - OCR Service API: http://localhost:8000/docs"
echo "  - AI LLM Service API: http://localhost:8001/docs"
echo "  - Test Interface: http://localhost:3000/test-ocr"
echo ""
echo "=================================="
