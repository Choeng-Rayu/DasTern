#!/bin/bash
# Quick test runner for OCR → AI pipeline
# This script runs the test and shows you the results

echo "=========================================="
echo "🚀 Running OCR → AI Pipeline Test"
echo "=========================================="
echo ""

cd /home/rayu/DasTern/OCR_Test_Space

# Check if AI service is running
echo "🔍 Checking AI service..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ AI service is running"
else
    echo "❌ AI service not running. Please start it first:"
    echo "   cd /home/rayu/DasTern/ai-llm-service"
    echo "   python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001 --reload"
    exit 1
fi

echo ""
echo "⏳ Running tests (this will take several minutes)..."
echo "   Each test takes 40-120 seconds due to CPU processing"
echo ""

# Run the test
python3 test_full_pipeline.py

echo ""
echo "=========================================="
echo "📁 Results saved to:"
echo "=========================================="
ls -lh results/result_*.json 2>/dev/null || echo "No result files found"

echo ""
echo "📋 To view a result:"
echo "   cat results/result_1.json | python3 -m json.tool"
echo ""
echo "📊 To see raw OCR input vs AI output:"
echo "   cat results/result_1.json | jq '.raw_ocr_input, .ai_enhanced_output'"
