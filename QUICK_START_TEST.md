# Quick Start Guide: Run and Test AI Reminder Service

## 🚀 Step 1: Start the Services

### Terminal 1: Start Ollama (if not running)
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

### Terminal 2: Start AI Service
```bash
cd /home/rayu/DasTern/ai-llm-service

# Activate virtual environment (if exists)
source venv/bin/activate 2>/dev/null || true

# Set environment variables
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b

# Start the service
python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001 --reload
```

**You should see:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:app.main_ollama:Starting Ollama AI Service...
INFO:app.main_ollama:Ollama endpoint: http://localhost:11434
INFO:app.main_ollama:Available Ollama models: ['llama3.2:3b', 'llama3.1:8b']
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

## 🧪 Step 2: Test the Service

### Test 1: Health Check (Quick)
```bash
# Open a new terminal and run:
curl http://localhost:8001/health
```

**Expected output:**
```json
{"status":"healthy","service":"ollama-ai-service","ollama_connected":true}
```

### Test 2: Simple Reminder Extraction
```bash
# Test with a simple medication
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{"raw_ocr_json": {"text": "Butylscopolami 5 viên | ល្ងាច | យប់"}}'
```

**Expected output (after 40-120 seconds):**
```json
{
  "medications": [
    {
      "name": "Butylscopolamine",
      "times": ["evening", "night"],
      "times_24h": ["18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "ល្ងាច | យប់"
    }
  ],
  "success": true,
  "error": null,
  "metadata": {
    "model": "llama3.2:3b",
    "attempts": 1
  }
}
```

### Test 3: Multiple Medications
```bash
# Test with structured table data
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{
    "raw_ocr_json": {
      "medications_table": [
        {
          "name": "Butylscopolamine 10mg",
          "qty": "14 គ្រាប់",
          "morning": "1",
          "noon": "-",
          "evening": "1",
          "night": "-"
        },
        {
          "name": "Omeprazole 20mg",
          "qty": "14 គ្រាប់",
          "morning": "1",
          "noon": "-",
          "evening": "1",
          "night": "-"
        }
      ]
    }
  }'
```

---

## 📱 Step 3: Run Test Scripts

### Option A: Quick Demonstration
```bash
cd /home/rayu/DasTern/OCR_Test_Space
python3 demo_working_flow.py
```

This shows the complete flow with example outputs (no actual API calls).

### Option B: Direct Ollama Test
```bash
cd /home/rayu/DasTern/OCR_Test_Space
python3 test_ollama_simple.py
```

This tests Ollama directly with a simple prompt (faster than full API).

### Option C: Full Pipeline Test
```bash
cd /home/rayu/DasTern/OCR_Test_Space
python3 test_full_pipeline.py
```

This tests the complete pipeline with real prescription data.

---

## 🔍 Step 4: Verify the Output

### Checklist for Valid Output:

✅ **JSON is valid** - No syntax errors  
✅ **success: true** - Processing succeeded  
✅ **medications array** - Contains at least one medication  
✅ **name field** - Medication name is corrected (e.g., "Butylscopolami" → "Butylscopolamine")  
✅ **times array** - Contains English time words (morning/noon/evening/night)  
✅ **times_24h array** - Matches times array with 08:00/12:00/18:00/21:00  
✅ **Khmer translated** - ល្ងាច → evening, យប់ → night, etc.

### Example Valid Response:
```json
{
  "medications": [
    {
      "name": "Butylscopolamine",
      "times": ["evening", "night"],
      "times_24h": ["18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "ល្ងាច | យប់"
    }
  ],
  "success": true,
  "error": null
}
```

---

## 🛠️ Step 5: Troubleshooting

### Issue: "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve
```

### Issue: "Connection refused" on port 8001
```bash
# Check if AI service is running
ps aux | grep uvicorn

# If not running, start it:
cd /home/rayu/DasTern/ai-llm-service
python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001
```

### Issue: Request timeout
- **Normal on CPU**: First request takes 40-120 seconds
- **Wait longer**: The model is processing
- **Check logs**: `tail -f /tmp/ai_service.log`

### Issue: Empty medications array
```bash
# Check the AI service logs
tail -20 /tmp/ai_service.log

# Look for:
# - "Successfully extracted X medications" (good)
# - "No valid medications found" (bad - check input)
# - "JSON parse error" (bad - check Ollama response)
```

---

## 📝 Step 6: Test with Your Own Data

### Create a test file:
```bash
cat > /tmp/my_test.json << 'EOF'
{
  "raw_ocr_json": {
    "text": "Your medication text here with ព្រឹក or ល្ងាច times"
  }
}
EOF
```

### Send the test:
```bash
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d @/tmp/my_test.json
```

---

## 🎯 Quick Reference Commands

```bash
# 1. Check health
curl http://localhost:8001/health

# 2. Test simple extraction
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{"raw_ocr_json":{"text":"Med | ល្ងាច | យប់"}}'

# 3. View service logs
tail -f /tmp/ai_service.log

# 4. Check Ollama models
curl http://localhost:11434/api/tags

# 5. Run demo
cd /home/rayu/DasTern/OCR_Test_Space && python3 demo_working_flow.py
```

---

## ✅ Success Criteria

You know it's working when:
1. ✅ Health check returns `{"status":"healthy"}`
2. ✅ Extract-reminders returns valid JSON
3. ✅ Medications have corrected names
4. ✅ Khmer times are translated to English
5. ✅ Times have matching 24h format (08:00, 12:00, 18:00, 21:00)

**Note**: Response time will be 40-120 seconds on CPU. This is normal!
