#!/bin/bash
# Test all prescription images in the test folder

echo "🧪 Testing OCR on All Prescription Images"
echo "=========================================="
echo ""

IMAGE_DIR="/home/rayu/DasTern/.ignore-ocr-service/images_for_Test_yu"
PYTHON="/home/rayu/DasTern/.venv/bin/python"
SCRIPT="/home/rayu/DasTern/test-ocr-standalone.py"

# Test each image
for img in "$IMAGE_DIR"/*.png; do
    if [ -f "$img" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Testing: $(basename "$img")"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        $PYTHON $SCRIPT "$img"
        
        echo ""
        echo "✅ Completed: $(basename "$img")"
        echo "📄 Results saved to: test_ocr_result.json"
        echo ""
        read -p "Press Enter to continue to next image..."
    fi
done

echo ""
echo "🎉 All images tested!"
