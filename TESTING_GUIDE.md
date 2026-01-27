# DasTern OCR Testing - Quick Start Guide

## ✅ Services Running

All three services are now running successfully in separate terminals:

### 1. OCR Service (Port 8000)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Engine**: RapidOCR (PaddleOCR models)
- **Status**: ✅ Running

### 2. AI LLM Service (Port 8001)
- **URL**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Model**: llama3.1:8b (via Ollama)
- **Status**: ⚠️ Running (pulling model in background)

### 3. Test Interface (Port 3000)
- **URL**: http://localhost:3000/test-ocr
- **Framework**: Next.js 16
- **Status**: ✅ Ready

## 🧪 Testing OCR Accuracy

### Step 1: Access the Test Interface
Open your browser and go to:
```
http://localhost:3000/test-ocr
```

### Step 2: Upload a Prescription Image
1. Click "Select Prescription Image"
2. Choose a prescription image from your computer
3. Supported formats: JPG, PNG, BMP, TIFF, WebP

### Step 3: Process with OCR
1. Click the "Process with OCR" button
2. Wait for processing (usually 2-10 seconds)
3. Review the results in three tabs:
   - **OCR Results**: Raw extracted text with confidence scores
   - **Prescription**: Structured medication data
   - **Reminders**: Suggested medication schedule

### Step 4: Evaluate Accuracy
Check these key metrics:
- **Text Extraction**: Are all words correctly recognized?
- **Confidence Scores**: Green (>90%), Yellow (70-90%), Red (<70%)
- **Structure**: Are medications properly identified?
- **Language Support**: English, Khmer, French

## 📊 Accuracy Indicators

### High Accuracy (Good)
- ✅ Confidence > 90%
- ✅ All medication names correct
- ✅ Dosages accurately extracted
- ✅ Doctor/patient info readable

### Medium Accuracy (Review Needed)
- ⚠️ Confidence 70-90%
- ⚠️ Some text unclear
- ⚠️ Manual verification recommended

### Low Accuracy (Poor)
- ❌ Confidence < 70%
- ❌ Missing or incorrect text
- ❌ Image quality issues
- ❌ Handwriting or unclear fonts

## 🔧 API Testing (Advanced)

### Test OCR Service Directly
```bash
# Upload an image for OCR processing
curl -X POST http://localhost:8000/ocr \
  -F "file=@/path/to/prescription.jpg"
```

### Test AI Enhancement
```bash
# Get AI-enhanced prescription data
curl -X POST http://localhost:8001/enhance \
  -H "Content-Type: application/json" \
  -d '{"ocr_data": {...}}'
```

## 🛠️ Troubleshooting

### OCR Service Issues
- Check terminal output for errors
- Verify RapidOCR is installed: `pip list | grep rapidocr`
- Test with high-quality images first

### AI Service Issues  
- Llama model may be downloading (check logs)
- Wait for "Model llama3.1:8b loaded successfully" message
- Check Ollama: `ollama list`

### Interface Issues
- Clear browser cache
- Check browser console (F12) for errors
- Ensure all services are running

## 📝 Service Management

### Stop All Services
Press `Ctrl+C` in each terminal running a service

### Restart Services
Use the startup scripts:
```bash
# Terminal 1
./start-ocr-manual.sh

# Terminal 2  
./start-ai-llm-manual.sh

# Terminal 3
cd ai_ocr_interface_test && npm run dev
```

### Check Service Status
```bash
# Check if services are running
lsof -ti:8000  # OCR service
lsof -ti:8001  # AI LLM service
lsof -ti:3000  # Next.js interface
```

## 📁 Test Images Location
Place your test prescription images in:
```
/home/rayu/DasTern/test_images/
```

## 🎯 Testing Checklist

- [ ] Upload clear, well-lit prescription image
- [ ] Verify all text is extracted
- [ ] Check confidence scores
- [ ] Compare with original image
- [ ] Test with different image qualities
- [ ] Test with multi-language prescriptions
- [ ] Test with handwritten prescriptions
- [ ] Review AI-enhanced structured data

## 💡 Tips for Better Accuracy

1. **Image Quality**
   - Use high resolution (300+ DPI)
   - Good lighting, no shadows
   - Straight orientation
   - Clear focus

2. **Document Type**
   - Printed prescriptions work best
   - Avoid handwritten if possible
   - Clean, unfolded paper

3. **Testing Strategy**
   - Start with typed prescriptions
   - Gradually test harder cases
   - Document failure patterns
   - Compare different OCR engines

---

**Current Setup**: Manual run with .venv (no Docker)
**OCR Engine**: RapidOCR (PaddleOCR models)  
**AI Model**: Llama 3.1 8B via Ollama
