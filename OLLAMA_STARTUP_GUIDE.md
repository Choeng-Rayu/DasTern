# 🚀 Running DasTern: Complete Setup Guide

## Prerequisites Check

✅ Ollama running with LLaMA models  
✅ Tesseract OCR installed  
✅ Python 3.8+ installed  
✅ Flutter SDK installed  

---

## Step 1: Start Ollama Server

**Terminal 1:**
```bash
# Start Ollama (if not already running)
ollama serve

# Expected output:
# INFO Ollama is running...
```

**Verify Ollama is ready:**
```bash
curl http://localhost:11434/api/tags | jq .
# Should show: llama3.1:8b and llama3.2:3b
```

---

## Step 2: Start OCR Service

**Terminal 2:**
```bash
cd /home/rayu/DasTern/ocr-service-anti

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Verify OCR Service:**
```bash
curl http://localhost:8000/api/v1/health | jq .
# Expected response:
# {
#   "status": "healthy",
#   "tesseract_available": true,
#   "languages_available": ["eng", "fra", "khm"],
#   "version": "1.0.0"
# }
```

---

## Step 3: Start Ollama AI Service

**Terminal 3:**
```bash
cd /home/rayu/DasTern/ai-llm-service

# Install dependencies (if needed)
pip install -r requirements.txt

# Start with Ollama model
python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001 --reload

# Expected output:
# INFO: Starting Ollama AI Service...
# INFO: Ollama endpoint: http://localhost:11434
# INFO: Default model: llama3.1:8b
# INFO: Available Ollama models: ['llama3.2:3b', 'llama3.1:8b']
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete
```

**Verify AI Service:**
```bash
curl http://localhost:8001/health | jq .
# Expected response:
# {
#   "status": "healthy",
#   "service": "ollama-ai-service",
#   "ollama_connected": true
# }
```

---

## Step 4: Verify Both Services

**Terminal 4 (Test Terminal):**

### 4a. Quick Health Check
```bash
# Check both services
echo "=== OCR Service ===" && \
curl -s http://localhost:8000/api/v1/health | jq . && \
echo -e "\n=== AI Service ===" && \
curl -s http://localhost:8001/health | jq .
```

### 4b. Test OCR Correction Route
```bash
curl -X POST http://localhost:8001/api/v1/correct \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Paracetamol 500mg - 1 tablet twice daily",
    "language": "en"
  }' | jq .
```

### 4c. Test Reminder Extraction
```bash
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Paracetamol 500mg - 1 tablet twice daily. Duration: 7 days",
    "language": "en"
  }' | jq .
```

---

## Step 5: Run Flutter App

**Terminal 5:**
```bash
cd /home/rayu/DasTern/ocr_ai_for_reminder

# Get dependencies
flutter pub get

# Run on device/emulator
flutter run

# Select device when prompted:
# [1] Android Emulator (emulator-5554)
# [2] (physical device)
# Choose your device
```

---

## Step 6: Configure App Settings

Once Flutter app launches:

### For Android Emulator
```
Config Tab → Service URLs

OCR Service URL: http://10.0.2.2:8000
AI Service URL: http://10.0.2.2:8001

Timeout: 60 seconds
```

### For Physical Phone (Same Network)
```
Config Tab → Service URLs

OCR Service URL: http://<YOUR_PC_IP>:8000
AI Service URL: http://<YOUR_PC_IP>:8001

Timeout: 60 seconds
```

**Find your PC IP:**
```bash
# Linux
hostname -I | awk '{print $1}'

# macOS
ifconfig | grep "inet " | grep -v "127.0.0.1"
```

---

## Step 7: Test the Complete Workflow

### In Flutter App:

1. **OCR Tab**
   - Tap "Pick Image"
   - Select a prescription image
   - Tap "Run OCR"
   - Wait 3-5 seconds
   - View extracted text

2. **AI Tab**
   - OCR text should auto-populate
   - Tap "Enhance Text" (uses Ollama)
   - View corrected text
   - Tap "Extract Reminders"
   - View medications and reminder schedule

3. **Config Tab**
   - View/modify service URLs
   - Check service status
   - Monitor response times

---

## Troubleshooting

### Issue: "Connection refused" errors

**Solution:**
```bash
# Check if services are running
lsof -i :8000  # OCR Service
lsof -i :8001  # AI Service

# If not running, start them (see Step 2 & 3)
```

### Issue: Ollama times out

**Solution:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama if needed
# (Terminal 1: Ctrl+C, then rerun)
```

### Issue: "Address already in use"

**Solution:**
```bash
# Kill process using the port
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
lsof -i :8001 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Then restart services
```

### Issue: Flutter can't reach services

**Solution - Emulator:**
```
Use 10.0.2.2 instead of localhost/127.0.0.1
```

**Solution - Physical Phone:**
```
Make sure PC and phone are on same WiFi
Use PC's actual IP address (not localhost)
```

### Issue: Ollama model is too slow

**Solution:**
```bash
# Switch to faster model
export OLLAMA_MODEL=llama3.2:3b

# Then restart AI Service (Terminal 3)
```

---

## File Structure for Reference

```
/home/rayu/DasTern/
├── ocr-service-anti/          # OCR Service (Port 8000)
│   ├── app/main.py           # FastAPI app
│   └── requirements.txt
│
├── ai-llm-service/            # AI Service (Port 8001)
│   ├── app/main_ollama.py     # Ollama-based main file
│   ├── app/main.py            # Alternative MT5 version
│   └── requirements.txt
│
└── ocr_ai_for_reminder/       # Flutter App
    ├── lib/main.dart          # Complete Flutter UI
    ├── pubspec.yaml
    └── android/ios/...
```

---

## API Endpoints Quick Reference

### OCR Service (Port 8000)
```
GET  /api/v1/health              # Health check
POST /api/v1/ocr                 # Upload image for OCR
```

### AI Service (Port 8001)
```
GET  /                           # Service info
GET  /health                     # Health check
POST /api/v1/correct             # Correct OCR text (Ollama)
POST /extract-reminders          # Extract reminders
POST /api/v1/chat                # Chat with medical assistant
POST /correct-ocr                # Simple correction
```

---

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| OCR Image Processing | 2-4s | Tesseract extraction |
| AI Text Correction | 5-10s | First token from Ollama |
| Reminder Extraction | 3-5s | Rule-based parsing |
| Total Pipeline | 10-20s | Full workflow |

---

## Monitor Running Services

**Check service health:**
```bash
# All in one command
echo "OCR: $(curl -s http://localhost:8000/api/v1/health | jq .status -r)" && \
echo "AI: $(curl -s http://localhost:8001/health | jq .status -r)" && \
echo "Ollama: $(curl -s http://localhost:11434/api/tags > /dev/null && echo 'OK' || echo 'DOWN')"
```

**View logs for debugging:**
```bash
# OCR Service logs (Terminal 2)
# Watch for errors and performance metrics

# AI Service logs (Terminal 3)
# Watch for Ollama connection issues

# Flutter app
# Check console for API call details
```

---

## Summary

| Step | What | Terminal | Time |
|------|------|----------|------|
| 1 | Start Ollama | Term 1 | 30s |
| 2 | Start OCR Service | Term 2 | 30s |
| 3 | Start AI Service | Term 3 | 1m |
| 4 | Test Services | Term 4 | 1m |
| 5 | Run Flutter App | Term 5 | 2m |
| 6 | Configure App | Phone | 1m |
| 7 | Test Workflow | Phone | 2m |

**Total Setup Time: ~10 minutes**

---

## Getting Started Now

Run these commands in order (in separate terminals):

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: OCR
cd /home/rayu/DasTern/ocr-service-anti && \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: AI
cd /home/rayu/DasTern/ai-llm-service && \
python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001 --reload

# Terminal 4: Flutter
cd /home/rayu/DasTern/ocr_ai_for_reminder && \
flutter run

# Terminal 5: Test (Optional)
cd /home/rayu/DasTern && \
python test_api_direct.py
```

---

**✅ System is ready to use!**
