# 🧪 Quick Test Guide - OCR Without Docker

## ⚡ Fastest Way to Test

### Option 1: Next.js UI (Mock Data - No OCR Engine Needed)
```bash
cd ai_ocr_interface_test
npm run dev
```
Then open: http://localhost:3000/test-ocr

✅ **Use this to test:**
- UI/UX of OCR interface
- Prescription data formatting
- Reminder schedule display
- No setup required!

---

### Option 2: Real OCR with Python (.venv)
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install OCR dependencies (takes 5-10 minutes)
pip install -r ocr-service/requirements.txt

# 3. Test with your prescription image
python test-ocr-standalone.py your_prescription.jpg

# Output saved to: test_ocr_result.json
```

✅ **Use this to test:**
- Real OCR extraction
- Text confidence scores
- Actual prescription parsing
- Reminder generation logic

---

## 📸 Sample Test Images

If you don't have a prescription image, you can:

1. **Create a sample text image** with this command:
```bash
convert -size 800x600 xc:white \
  -font Arial -pointsize 20 -fill black \
  -draw "text 50,50 'Patient: John Doe'" \
  -draw "text 50,100 'Date: 26/01/2026'" \
  -draw "text 50,150 'Dr. Sarah Johnson'" \
  -draw "text 50,200 'Amoxicillin 500mg'" \
  -draw "text 50,250 'Take 1 tablet 3 times daily'" \
  -draw "text 50,300 'After meals for 7 days'" \
  sample_prescription.png
```

2. **Or download from:**
   - https://via.placeholder.com/800x600/ffffff/000000?text=Prescription+Sample

---

## 🎯 What Each Test Shows

### Next.js UI Test Output:
- ✅ Patient information display
- ✅ Medication cards
- ✅ Dosage instructions
- ✅ Reminder schedule with times
- ✅ OCR confidence badges
- ✅ Tab navigation

### Python Script Output:
```
==========================================================
  OCR STANDALONE TEST - NO DOCKER, NO DATABASE
==========================================================

📸 Testing OCR on: prescription.jpg

==========================================================
  STEP 1: OCR EXTRACTION
==========================================================

⏳ Running PaddleOCR extraction...
✅ OCR completed!
   - Language: en
   - Confidence: 90.00%
   - Blocks detected: 14

==========================================================
  STEP 2: EXTRACTED TEXT BLOCKS
==========================================================

 1. [95.0%] Patient Name: John Doe
 2. [92.0%] Date: 26/01/2026
 3. [88.0%] Dr. Sarah Johnson
...

==========================================================
  STEP 3: PRESCRIPTION FORMATTING
==========================================================

📋 PRESCRIPTION DATA:
{
  "patient_info": {...},
  "medications": [...],
  "reminder_schedule": [...]
}

==========================================================
  STEP 4: REMINDER SCHEDULE
==========================================================

⏰ Medication Reminders:

1. ⏰ 08:00 - Amoxicillin 500mg after breakfast
   Status: ✅ Enabled

2. ⏰ 14:00 - Amoxicillin 500mg after lunch
   Status: ✅ Enabled
...
```

---

## 🔍 Checking Reminder Format

### Expected Reminder Structure:
```json
{
  "time": "08:00",
  "instruction": "Amoxicillin 500mg - 1 tablet after breakfast",
  "enabled": true
}
```

### Timing Keywords Detected:
- "morning" / "breakfast" → 08:00
- "noon" / "lunch" → 12:00 / 14:00
- "evening" / "dinner" → 18:00
- "night" / "bedtime" → 21:00
- "twice daily" → 09:00, 21:00
- "3 times daily" → 08:00, 14:00, 20:00

---

## ⚠️ Important Notes

### This Testing Does NOT Require:
- ❌ Docker containers
- ❌ Database connection
- ❌ Backend services running
- ❌ AI LLM service
- ❌ Network access

### This Testing ONLY Checks:
- ✅ OCR text extraction
- ✅ Data formatting logic
- ✅ Reminder generation rules
- ✅ UI display
- ✅ JSON structure

---

## 🐛 Troubleshooting

### PaddlePaddle Won't Install?
```bash
# Use minimal requirements (Tesseract instead)
pip install -r ocr-service/requirements-minimal.txt
```

### Port 3000 Already in Use?
```bash
# Kill existing process
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Virtual Environment Not Activating?
```bash
# Deactivate first
deactivate

# Remove and recreate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

---

## ✅ Success Checklist

After testing, you should be able to:

- [ ] Upload prescription image in UI
- [ ] See extracted text blocks
- [ ] View formatted prescription data
- [ ] See medication cards with dosage
- [ ] View reminder schedule with specific times
- [ ] Switch between tabs (OCR/Prescription/Reminders)
- [ ] See confidence scores for each text block
- [ ] Export/view results as JSON

---

## 📊 Performance Expectations

| Task | Time |
|------|------|
| Next.js dev server start | ~5 seconds |
| OCR dependencies install | ~5-10 minutes |
| Single image OCR processing | ~2-5 seconds |
| UI page load | Instant |

---

## 🚀 Next Steps After Testing

Once you've verified OCR and formatting work:

1. **Integrate with Backend:**
   - Connect Next.js to OCR service API
   - Add real-time processing

2. **Add Database Storage:**
   - Save prescriptions to PostgreSQL
   - Link with user accounts

3. **Deploy with Docker:**
   - Use full docker-compose.yml
   - Enable all services

But for NOW, just test locally with .venv! 🎉
