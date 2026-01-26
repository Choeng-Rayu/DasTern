#!/bin/bash
# Start OCR Test Interface
# No Docker, No Database required!

echo "🚀 Starting OCR Test Interface..."
echo ""

cd /home/rayu/DasTern/ai_ocr_interface_test

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies first..."
    npm install
    echo ""
fi

echo "🌐 Starting Next.js development server..."
echo ""
npm run dev

# Server will be available at:
# http://localhost:3000/test-ocr
