#!/bin/bash

# DasTern Services Management Script

echo "=== DasTern Services Status ==="
echo

# Check OCR Service
echo "🔍 OCR Service (Port 8004):"
if curl -s http://localhost:8004/ > /dev/null; then
    echo "   ✅ Running - $(curl -s http://localhost:8004/ | jq -r '.status' 2>/dev/null || echo 'OK')"
else
    echo "   ❌ Not running"
fi

# Check AI Service
echo "🤖 AI Service (Port 8005):"
if curl -s http://localhost:8005/ > /dev/null; then
    echo "   ✅ Running - $(curl -s http://localhost:8005/ | jq -r '.status' 2>/dev/null || echo 'OK')"
else
    echo "   ❌ Not running"
fi

# Check Backend
echo "🌐 Backend (Port 3000):"
if curl -s http://localhost:3000/ > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi

# Check Ollama
echo "🦙 Ollama (Port 11434):"
if curl -s http://localhost:11434/ > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi

echo
echo "=== Service URLs ==="
echo "OCR Service:    http://localhost:8004"
echo "AI Service:     http://localhost:8005"
echo "Backend:        http://localhost:3000"
echo "Ollama:         http://localhost:11434"
echo
echo "=== Logs ==="
echo "OCR logs:       tail -f /home/rayu/DasTern/ocr-service/ocr.log"
echo "AI logs:        tail -f /home/rayu/DasTern/ai-llm-service/ai.log"
echo "Backend logs:   tail -f /home/rayu/DasTern/backend-nextjs/backend.log"
echo "Ollama logs:    tail -f /home/rayu/DasTern/ollama.log"
