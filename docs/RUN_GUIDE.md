# Step-by-Step Guide: Run OCR + AI Services and Test Images

## 🎯 Overview

**Goal**: Process prescription images through OCR → AI → Get structured reminders

**Services**:
- OCR Service (port 8000): Extracts text from images
- AI Service (port 8001): Processes text into structured JSON

---

## 🚀 Method 1: Automatic (Recommended)

### Step 1: Start Both Services
```bash
cd /home/rayu/DasTern
./start_services.sh
```

This will:
- ✅ Check if services are already running
- 🚀 Start OCR Service on port 8000 (if not running)
- 🚀 Start AI Service on port 8001 (if not running)
- ⏳ Wait for services to be ready
- 📊 Show status

### Step 2: Run the Test
```bash
cd /home/rayu/DasTern/OCR_Test_Space
./run_pipeline_test.sh
```

This will:
- ✅ Check services are running
- 📄 Send images to OCR service
- 🤖 Send OCR output to AI service
- 💾 Save results to `results/result_1.json`, `result_2.json`, etc.
- 📊 Show summary

---

## 📝 Method 2: Manual Step-by-Step

### Terminal 1: Start OCR Service
```bash
# Navigate to OCR service
cd /home/rayu/DasTern/ocr-service

# Activate virtual environment (if exists)
source venv/bin/activate 2>/dev/null || true

# Start the service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Started server process [XXXX]
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify it's running** (in another terminal):
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","tesseract":true}
```

---

### Terminal 2: Start AI Service
```bash
# Navigate to AI service
cd /home/rayu/DasTern/ai-llm-service

# Activate virtual environment (if exists)
source venv/bin/activate 2>/dev/null || true

# Set environment variables
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b

# Start the service
python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001

# You should see:
# INFO:     Started server process [XXXX]
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:app.main_ollama:Available Ollama models: ['llama3.2:3b', 'llama3.1:8b']
```

**Verify it's running** (in another terminal):
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy","ollama_connected":true}
```

---

### Terminal 3: Run the Test
```bash
# Navigate to test directory
cd /home/rayu/DasTern/OCR_Test_Space

# Run the complete pipeline test
python3 test_full_pipeline.py
```

**What happens:**
1. ✅ Checks both services are running
2. 📄 **Image 1** → OCR → AI → Save result_1.json
3. 📄 **Image 2** → OCR → AI → Save result_2.json
4. 📄 **Image 3** → OCR → AI → Save result_3.json
5. 📊 Shows summary

**Time**: ~3-6 minutes total (40-120 seconds per image)

---

## 📁 Viewing Results

### After the test completes, view results:

```bash
# List result files
ls -lh /home/rayu/DasTern/OCR_Test_Space/results/

# View a specific result
cat /home/rayu/DasTern/OCR_Test_Space/results/result_1.json | python3 -m json.tool

# View just the OCR output
cat /home/rayu/DasTern/OCR_Test_Space/results/result_1.json | jq '.step_1_ocr_output'

# View just the AI output
cat /home/rayu/DasTern/OCR_Test_Space/results/result_1.json | jq '.step_2_ai_output'

# Compare OCR vs AI
cat /home/rayu/DasTern/OCR_Test_Space/results/result_1.json | jq '{
  ocr_text: .step_1_ocr_output.raw_data[0].text,
  ai_medications: .step_2_ai_output.medications
}'
```

---

## 🔍 Quick Test (Single Image)

If you want to test just one image quickly:

```bash
# Test Image 1 only
cd /home/rayu/DasTern/OCR_Test_Space

# Step 1: Send to OCR
curl -X POST http://localhost:8000/api/v1/ocr/extract \
  -F "file=@images/image1.png" \
  -F "languages=khm+eng+fra" > /tmp/ocr_result.json

# View OCR result
cat /tmp/ocr_result.json | jq '.stats, .raw[0:3]'

# Step 2: Send OCR result to AI
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d @/tmp/ocr_result.json > /tmp/ai_result.json

# View AI result
cat /tmp/ai_result.json | jq '.medications'
```

---

## 🛠️ Troubleshooting

### Services won't start?
```bash
# Check if ports are already in use
lsof -i :8000  # OCR port
lsof -i :8001  # AI port

# Kill existing processes if needed
pkill -f "uvicorn.*port 8000"
pkill -f "uvicorn.*port 8001"
```

### OCR Service fails?
```bash
# Check Tesseract is installed
tesseract --version

# Check log
cat /tmp/ocr_service.log
```

### AI Service fails?
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve

# Check log
cat /tmp/ai_service.log
```

### Test times out?
- **Normal**: AI takes 40-120 seconds per image on CPU
- **Don't cancel**: Wait for it to complete
- **Check logs**: `tail -f /tmp/ai_service.log`

---

## 📊 Expected Output

### Result File Structure:
```json
{
  "test_info": {
    "result_number": 1,
    "image_name": "Khmer-Soviet Hospital (Chronic Cystitis)",
    "timestamp": "2026-01-30T..."
  },
  "step_1_ocr_output": {
    "description": "Raw OCR from OCR Service",
    "success": true,
    "total_elements": 45,
    "stats": {
      "overall_confidence": 0.73,
      "image_width": 1200,
      "image_height": 1600
    },
    "raw_data": [...]
  },
  "step_2_ai_output": {
    "description": "AI-enhanced from AI Service",
    "success": true,
    "medications": [
      {
        "name": "Butylscopolamine",
        "times": ["evening", "night"],
        "times_24h": ["18:00", "21:00"],
        "repeat": "daily",
        "duration_days": null,
        "notes": "ល្ងាច | យប់"
      }
    ]
  }
}
```

---

## 🎉 Success!

When you see:
```
✅ PIPELINE SUCCESS for Image 1: Khmer-Soviet Hospital
✅ PIPELINE SUCCESS for Image 2: Sok Heng Polyclinic
✅ PIPELINE SUCCESS for Image 3: Khmer-Soviet Hospital
```

Your results are saved and ready for analysis!
