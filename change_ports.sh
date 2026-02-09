#!/bin/bash
# Quick Port Configuration Script
# Usage: ./change_ports.sh [OCR_PORT] [AI_PORT]
# Example: ./change_ports.sh 8003 8002

NEW_OCR_PORT=${1:-8000}
NEW_AI_PORT=${2:-8001}

echo "🔧 Changing service ports..."
echo "   OCR Service: $NEW_OCR_PORT"
echo "   AI Service:  $NEW_AI_PORT"
echo ""

# Update ai-llm-service
if [ -f "ai-llm-service/.env" ]; then
    sed -i "s/^AI_SERVICE_PORT=.*/AI_SERVICE_PORT=$NEW_AI_PORT/" ai-llm-service/.env
    echo "✅ Updated ai-llm-service/.env"
else
    echo "❌ ai-llm-service/.env not found"
fi

# Update ocr-service-anti
if [ -f "ocr-service-anti/.env" ]; then
    sed -i "s/^OCR_SERVICE_PORT=.*/OCR_SERVICE_PORT=$NEW_OCR_PORT/" ocr-service-anti/.env
    sed -i "s|^AI_LLM_SERVICE_URL=.*|AI_LLM_SERVICE_URL=http://localhost:$NEW_AI_PORT|" ocr-service-anti/.env
    echo "✅ Updated ocr-service-anti/.env"
else
    echo "❌ ocr-service-anti/.env not found"
fi

# Update Flutter app
if [ -f "ocr_ai_for_reminder/.env" ]; then
    sed -i "s/^OCR_SERVICE_PORT=.*/OCR_SERVICE_PORT=$NEW_OCR_PORT/" ocr_ai_for_reminder/.env
    sed -i "s/^AI_SERVICE_PORT=.*/AI_SERVICE_PORT=$NEW_AI_PORT/" ocr_ai_for_reminder/.env
    sed -i "s|^OCR_SERVICE_URL=.*|OCR_SERVICE_URL=http://localhost:$NEW_OCR_PORT|" ocr_ai_for_reminder/.env
    sed -i "s|^AI_LLM_SERVICE_URL=.*|AI_LLM_SERVICE_URL=http://localhost:$NEW_AI_PORT|" ocr_ai_for_reminder/.env
    echo "✅ Updated ocr_ai_for_reminder/.env"
else
    echo "❌ ocr_ai_for_reminder/.env not found"
fi

echo ""
echo "✅ Port configuration updated successfully!"
echo ""
echo "📋 New Configuration:"
echo "   OCR Service:     http://localhost:$NEW_OCR_PORT"
echo "   AI-LLM Service:  http://localhost:$NEW_AI_PORT"
echo ""
echo "⚠️  Please restart all services for changes to take effect:"
echo "   1. Stop any running services (Ctrl+C)"
echo "   2. Start OCR service:  cd ocr-service-anti && python main.py"
echo "   3. Start AI service:   cd ai-llm-service && python app/main_ollama.py"
echo "   4. Rebuild Flutter app if needed"
