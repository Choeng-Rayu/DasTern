# 🎬 DEMO QUICK REFERENCE CARD

## Print this and keep it next to you during the demo!

---

### ⚡ Quick Start (5 mins before demo)
```bash
cd /Users/macbook/CADT/DasTern
./start_all_services.sh          # Start all services
./test_demo.sh                    # Verify everything works
```

---

### 📋 Demo Order (20 mins)

#### 1. INTRO (2 mins)
> "We built 3 components: OCR Service (extracts text), AI Service (corrects & structures), Flutter App (user interface)"

#### 2. OCR SERVICE (5 mins)
```bash
# Health check
curl http://127.0.0.1:8000/api/v1/health | jq

# Process image (replace path!)
curl -X POST http://127.0.0.1:8000/api/v1/ocr \
  -F "file=@/path/to/prescription.jpg" | jq
```

**Say:** "OCR extracts text from images in English, Khmer, and French"

#### 3. AI SERVICE (7 mins)
```bash
# Status
curl http://127.0.0.1:8001/ | jq

# Correct OCR errors
curl -X POST http://127.0.0.1:8001/correct-ocr \
  -H "Content-Type: application/json" \
  -d '{"text":"Paracetam0l 500mg","language":"en"}' | jq

# Extract reminders (THE IMPRESSIVE PART!)
curl -X POST http://127.0.0.1:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{"raw_ocr_json":{"full_text":"Amoxicillin 500mg\nTake 3 times daily for 7 days"}}' | jq
```

**Say:** "AI converts '3 times daily' to actual times: 08:00, 12:00, 18:00"

#### 4. FLUTTER APP (6 mins)
```bash
cd ocr_ai_for_reminder
flutter run -d macos
```

**Show:**
1. Upload image
2. Watch real-time processing
3. See extracted medications
4. Point out generated schedules

---

### 🔥 Key Demo Talking Points

✅ **Privacy:** "Runs 100% locally, no data sent to cloud"
✅ **Cost:** "No API fees - Ollama is free and open source"
✅ **Speed:** "Full processing in 5-7 seconds"
✅ **Languages:** "Supports 126 languages, optimized for eng+khm+fra"
✅ **Model:** "Uses lightweight 3B model - runs on consumer hardware"

---

### 🚨 Emergency Commands (if something breaks)

```bash
# Restart services
kill $(lsof -ti:8000)  # Kill OCR service
kill $(lsof -ti:8001)  # Kill AI service
./start_all_services.sh

# Check what's running
lsof -i :8000
lsof -i :8001
lsof -i :11434

# View logs
tail -f /tmp/ocr_service.log
tail -f /tmp/ai_service.log
```

---

### 💡 Common Questions - Quick Answers

**Q: Why not use OpenAI?**
A: Privacy, cost, and offline capability

**Q: How accurate is OCR?**
A: 95%+ on typed text, AI corrects errors

**Q: Can it handle handwriting?**
A: Typed text best, handwriting needs training

**Q: What languages?**
A: 126 languages, currently eng+khm+fra

**Q: How fast?**
A: 5-7 seconds end-to-end per prescription

**Q: Can it scale?**
A: Yes - can process 10-20 prescriptions/minute

---

### 📸 Browser Tabs to Have Open

1. **OCR API Docs:** http://127.0.0.1:8000/docs
2. **AI API Docs:** http://127.0.0.1:8001/docs
3. **This guide:** /Users/macbook/CADT/DasTern/DEMO_QUICK_REF.md
4. **Full script:** /Users/macbook/CADT/DasTern/DEMO_SCRIPT.md

---

### 🎯 Success = Show These 4 Things

1. ✅ OCR extracts text from image
2. ✅ AI corrects OCR errors
3. ✅ AI generates medication schedule with times
4. ✅ Flutter app shows full workflow

---

**You got this! 🚀**
