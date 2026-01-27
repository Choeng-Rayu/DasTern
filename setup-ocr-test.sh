#!/bin/bash
# Quick setup script for OCR test interface

echo "================================"
echo "  DasTern OCR Test Setup"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -d "ai_ocr_interface_test" ]; then
    echo "❌ Error: ai_ocr_interface_test directory not found"
    echo "   Please run this script from the DasTern project root"
    exit 1
fi

echo "📦 Installing Next.js dependencies..."
cd ai_ocr_interface_test
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "================================"
    echo "  Setup Complete!"
    echo "================================"
    echo ""
    echo "To start the test interface:"
    echo "  cd ai_ocr_interface_test"
    echo "  npm run dev"
    echo ""
    echo "Then open: http://localhost:3000/test-ocr"
    echo ""
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
