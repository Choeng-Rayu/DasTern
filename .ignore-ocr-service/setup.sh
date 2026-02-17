#!/bin/bash
# Setup script for OCR Backend

echo "🚀 Setting up OCR Backend for Prescription Scanning"
echo "=================================================="

# Create virtual environment
echo ""
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Tesseract language data
echo ""
echo "🌐 Checking Tesseract installation..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract found at: $(which tesseract)"
    echo "   Version: $(tesseract --version | head -1)"
else
    echo "❌ Tesseract not found. Please install it:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   macOS: brew install tesseract"
fi

# Check for language data
echo ""
echo "📝 Checking Tesseract language data..."

check_lang() {
    if tesseract --list-langs 2>/dev/null | grep -q "$1"; then
        echo "✅ $1 language data found"
        return 0
    else
        echo "❌ $1 language data NOT found"
        return 1
    fi
}

check_lang "eng"
check_lang "khm" || echo "   Install: sudo apt-get install tesseract-ocr-khm"
check_lang "fra" || echo "   Install: sudo apt-get install tesseract-ocr-fra"

# Download MT5 model (optional, first-run will auto-download)
echo ""
echo "🤖 MT5 Model Setup..."
echo "   The MT5-small model will be downloaded on first use (~1.2GB)"
echo "   To pre-download, run:"
echo "   python -c \"from transformers import MT5Tokenizer, MT5ForConditionalGeneration; MT5Tokenizer.from_pretrained('google/mt5-small'); MT5ForConditionalGeneration.from_pretrained('google/mt5-small')\""

# Create directories
echo ""
echo "📁 Ensuring directory structure..."
mkdir -p ai/mt5/tokenizer ai/mt5/model ai/fine_tune tessdata

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"

