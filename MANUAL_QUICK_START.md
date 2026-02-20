# Quick Start Reference - Manual Setup

**Print this and keep it next to you!**

---

## Opening VSCode & Starting (4 Terminals)

### Terminal 1: Ollama
```bash
ollama serve
```
**Wait for:** `Listening on 127.0.0.1:11434`

---

### Terminal 2: OCR Service
```bash
cd /Users/macbook/CADT/DasTern/ocr-service-anti
source venv/bin/activate
python main.py 8000
```
**Wait for:** `Uvicorn running on http://127.0.0.1:8000`

**Verify:**
```bash
curl http://127.0.0.1:8000/health
```

---

### Terminal 3: AI Service
```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434
python app/main_ollama.py
```
**Wait for:** `Uvicorn running on http://127.0.0.1:8001`

**Verify:**
```bash
curl http://127.0.0.1:8001/health
```

---

### Terminal 4: Flutter App
```bash
cd /Users/macbook/CADT/DasTern/ocr_ai_for_reminder
flutter run -d macos
```

**Wait for app window to open.**

---

## Quick Health Check (All Services)

```bash
# Copy-paste this entire block:
echo "Checking Ollama..." && curl -s http://localhost:11434/api/tags | head -5 && \
echo -e "\nChecking OCR..." && curl -s http://127.0.0.1:8000/health && \
echo -e "\nChecking AI..." && curl -s http://127.0.0.1:8001/health
```

**All should return JSON responses ✅**

---

## Using the System

### Method 1: Flutter App (Easy)
1. Click "Upload Prescription"
2. Select image
3. Wait for processing
4. View extracted medications

### Method 2: Manual curl (Learning)

**Step 1: Extract text from image**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ocr" \
  -F "file=@/path/to/prescription.jpg" > ocr_output.json
```

**Step 2: Organize with AI**
```bash
curl -X POST "http://127.0.0.1:8001/extract-reminders" \
  -H "Content-Type: application/json" \
  -d @ocr_output.json
```

---

## Stopping Services

```bash
# In each terminal, press:
Ctrl+C

# Or forcefully kill all:
kill $(lsof -t -i :8000 :8001 :11434)
```

---

## Troubleshooting

### "Address already in use"
```bash
kill $(lsof -t -i :8000)  # OCR
kill $(lsof -t -i :8001)  # AI
kill $(lsof -t -i :11434) # Ollama
```

### "Connection refused"
```bash
# Check what's running:
lsof -i :8000
lsof -i :8001
lsof -i :11434
```

### "Tesseract not found"
```bash
brew install tesseract tesseract-lang
tesseract --version  # Verify
```

### "Model not found"
```bash
ollama serve  # In one terminal
ollama pull llama3.2:3b  # In another
```

---

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| OCR | 8000 | http://127.0.0.1:8000 |
| AI | 8001 | http://127.0.0.1:8001 |
| Ollama | 11434 | http://localhost:11434 |

---

## API Documentation

- **OCR Docs:** http://127.0.0.1:8000/docs
- **AI Docs:** http://127.0.0.1:8001/docs

---

## Sample Test Commands

### Test OCR Error Correction
```bash
curl -X POST http://127.0.0.1:8001/correct-ocr \
  -H "Content-Type: application/json" \
  -d '{"text":"Paracetam0l 50Omg","language":"en"}'
```

### Test Medication Extraction
```bash
curl -X POST http://127.0.0.1:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{"raw_ocr_json":{"full_text":"Paracetamol 500mg Take 3 times daily for 5 days"}}'
```

---

## Data Flow Summary

```
Image → OCR Service → Text
           ↓
Text → AI Service → Organized Medications
           ↓
Flutter App → Display to User
```

---

## First Time Setup Only

```bash
# 1. Install dependencies
brew install tesseract tesseract-lang ollama

# 2. Download AI model (one-time, ~2GB)
ollama serve & ollama pull llama3.2:3b

# 3. Setup OCR venv
cd ocr-service-anti
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 4. Setup AI venv
cd ../ai-llm-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 5. Setup Flutter
cd ../ocr_ai_for_reminder
flutter pub get
```

---

**For detailed guide, see:** `MANUAL_SETUP_GUIDE.md`

**For automated startup, use:** `./start_all_services.sh`
