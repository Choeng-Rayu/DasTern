#!/bin/bash
# Quick Demo Test Script
# Run this before your demo to make sure everything works

set -e  # Exit on error

echo "🧪 Testing DasTern Services for Demo..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: OCR Service Health
echo -e "${YELLOW}Test 1: OCR Service Health${NC}"
RESPONSE=$(curl -s http://127.0.0.1:8000/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ OCR Service is healthy${NC}"
else
    echo -e "${RED}❌ OCR Service failed${NC}"
    exit 1
fi
echo ""

# Test 2: OCR Service with Tesseract
echo -e "${YELLOW}Test 2: OCR Service Tesseract Check${NC}"
RESPONSE=$(curl -s http://127.0.0.1:8000/api/v1/health)
if echo "$RESPONSE" | grep -q "tesseract_available.*true"; then
    echo -e "${GREEN}✅ Tesseract is available${NC}"
    echo "$RESPONSE" | grep -o '"languages_available":\[[^]]*\]' | head -c 200
    echo "..."
else
    echo -e "${RED}❌ Tesseract not available${NC}"
    exit 1
fi
echo ""

# Test 3: AI Service Health
echo -e "${YELLOW}Test 3: AI Service Health${NC}"
RESPONSE=$(curl -s http://127.0.0.1:8001/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ AI Service is healthy${NC}"
else
    echo -e "${RED}❌ AI Service failed${NC}"
    exit 1
fi
echo ""

# Test 4: AI Service Model Check
echo -e "${YELLOW}Test 4: AI Service Model Check${NC}"
RESPONSE=$(curl -s http://127.0.0.1:8001/)
if echo "$RESPONSE" | grep -q "llama3.2:3b"; then
    echo -e "${GREEN}✅ Ollama llama3.2:3b is loaded${NC}"
    echo "$RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Model not loaded${NC}"
    exit 1
fi
echo ""

# Test 5: OCR Correction
echo -e "${YELLOW}Test 5: AI OCR Correction${NC}"
RESPONSE=$(curl -s -X POST "http://127.0.0.1:8001/correct-ocr" \
  -H "Content-Type: application/json" \
  -d '{"text": "Paracetam0l 500mg", "language": "en"}')
if echo "$RESPONSE" | grep -q "Paracetamol"; then
    echo -e "${GREEN}✅ OCR correction works${NC}"
    echo "$RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ OCR correction failed${NC}"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# Test 6: Reminder Extraction
echo -e "${YELLOW}Test 6: Reminder Extraction${NC}"
RESPONSE=$(curl -s -X POST "http://127.0.0.1:8001/extract-reminders" \
  -H "Content-Type: application/json" \
  -d '{"raw_ocr_json": {"full_text": "Amoxicillin 500mg Take 1 capsule 3 times daily for 7 days"}}')
if echo "$RESPONSE" | grep -q "medications"; then
    echo -e "${GREEN}✅ Reminder extraction works${NC}"
    echo "$RESPONSE" | python3 -m json.tool | head -30
else
    echo -e "${RED}❌ Reminder extraction failed${NC}"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# Test 7: Ollama Direct
echo -e "${YELLOW}Test 7: Ollama Direct Check${NC}"
RESPONSE=$(curl -s http://localhost:11434/api/tags)
if echo "$RESPONSE" | grep -q "llama3.2:3b"; then
    echo -e "${GREEN}✅ Ollama has llama3.2:3b model${NC}"
    echo "$RESPONSE" | python3 -c "import json, sys; models = json.load(sys.stdin)['models']; print('\n'.join([m['name'] for m in models]))"
else
    echo -e "${RED}❌ Ollama model not found${NC}"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 All Tests Passed! Ready for Demo!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Service Status:"
echo "   • OCR Service:  http://127.0.0.1:8000"
echo "   • AI Service:   http://127.0.0.1:8001"
echo "   • Ollama:       http://localhost:11434"
echo ""
echo "📚 API Documentation:"
echo "   • OCR Docs:     http://127.0.0.1:8000/docs"
echo "   • AI Docs:      http://127.0.0.1:8001/docs"
echo ""
echo "🚀 To run Flutter app:"
echo "   cd ocr_ai_for_reminder && flutter run -d macos"
echo ""
