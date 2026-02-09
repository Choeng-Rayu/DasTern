#!/bin/bash
# Complete Pipeline Test Runner
# Runs: Image → OCR Service → AI Service → Results

echo "=========================================="
echo "🚀 Complete Pipeline Test"
echo "   Image → OCR → AI → Results"
echo "=========================================="
echo ""

cd /home/rayu/DasTern/OCR_Test_Space

# Check if services are running
echo "🔍 Checking services..."

# Check OCR service
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ OCR Service (port 8000): Running"
else
    echo "❌ OCR Service (port 8000): Not running"
    echo "   Start with: cd /home/rayu/DasTern/ocr-service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

# Check AI service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ AI Service (port 8001): Running"
else
    echo "❌ AI Service (port 8001): Not running"
    echo "   Start with: cd /home/rayu/DasTern/ai-llm-service && python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001"
    exit 1
fi

echo ""
echo "⏳ Running pipeline tests..."
echo "   This will take several minutes (40-120s per image)"
echo ""

# Run the test
python3 test_full_pipeline.py

echo ""
echo "=========================================="
echo "📁 Results saved to:"
echo "=========================================="
ls -lh results/result_*.json 2>/dev/null || echo "No result files found"

echo ""
echo "📋 To view results:"
echo "   # Full result:"
echo "   cat results/result_1.json | python3 -m json.tool"
echo ""
echo "   # Just OCR output:"
echo "   cat results/result_1.json | jq '.step_1_ocr_output'"
echo ""
echo "   # Just AI output:"
echo "   cat results/result_1.json | jq '.step_2_ai_output'"
echo ""
echo "   # Compare both:"
echo "   cat results/result_1.json | jq '{ocr: .step_1_ocr_output.stats, ai: .step_2_ai_output.medications}'"
