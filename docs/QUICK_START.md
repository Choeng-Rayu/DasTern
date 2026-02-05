# Quick Start Guide - Prescription to Reminder

## 🚀 What You Can Do Now

Your DasTern system can now automatically convert Cambodian prescription images into medication reminders!

## 📋 Example Prescription Processing

### Input (Prescription Image)
- **Hospital**: Khmer-Soviet Friendship Hospital
- **Patient**: ហុ ចាន (Age 19)
- **Diagnosis**: Chronic Cystitis
- **Medications**: 4 drugs with specific timing

### Output (Generated Reminders)
```json
{
  "success": true,
  "medications_count": 4,
  "reminders_count": 10,
  "reminders": [
    {
      "medication_name": "Butylscopolamine 10mg",
      "time_slot": "morning",
      "scheduled_time": "08:00",
      "dose_amount": 1,
      "notification_title": "Time to take Butylscopolamine 10mg",
      "notification_body": "Take 1 Butylscopolamine 10mg (10mg) - Take before meals"
    },
    ... 9 more reminders
  ]
}
```

## 🔧 How to Use

### 1. Start the Services

```bash
# Start all services
docker-compose up -d

# Or start individually:
# OCR Service (Port 8000)
cd ocr-service && python3 -m app.main

# AI Service (Port 8001)
cd ai-llm-service && python3 -m app.main

# Backend (Port 3000)
cd backend-nextjs && npm run dev
```

### 2. Upload a Prescription

**Using curl:**
```bash
curl -X POST http://localhost:3000/api/prescriptions/upload \
  -F "image=@your_prescription.jpg" \
  -F "patient_id=your-patient-uuid"
```

**Using the Mobile App:**
- Open the app
- Go to "Scan Prescription"
- Take photo or upload image
- System automatically creates reminders!

### 3. Check Generated Reminders

The system will return:
- ✅ Prescription ID
- ✅ Extracted medications (4 drugs)
- ✅ Generated reminders (10 reminders)
- ✅ AI confidence score
- ✅ Notification messages

## 🌍 Supported Languages

### Khmer (Cambodian)
- ព្រឹក → Morning (08:00)
- ថ្ងៃត្រង់ → Noon (12:00)
- ល្ងាច → Evening (18:00)
- យប់ → Night (21:00)

### French
- matin → Morning (08:00)
- midi → Noon (12:00)
- soir → Evening (18:00)
- nuit → Night (21:00)

### English
- morning → 08:00
- noon → 12:00
- evening → 18:00
- night → 21:00

## 📊 Test Results

From the test with your prescription images:

```
✅ Successfully processed prescription
✅ Extracted 4 medications
✅ Generated 10 reminders
✅ All validations passed
✅ Time slots correctly mapped
✅ Notifications generated
```

## 🔍 API Endpoints

### Main Endpoint (Recommended)
```
POST /api/prescriptions/upload
```
Full processing: Image → OCR → AI → Database → Reminders

### Direct AI Processing
```
POST /api/v1/prescription/enhance-and-generate-reminders
```
Use when you already have OCR text

### Health Checks
```
GET /health                    # AI Service
GET /api/health               # Backend
```

## 🛠️ Configuration

### Environment Variables
```bash
# .env file
OCR_SERVICE_URL=http://ocr-service:8000
AI_SERVICE_URL=http://ai-llm-service:8001
DATABASE_URL=postgresql://user:pass@localhost:5432/dastern
```

### Time Slot Customization
Edit `/ai-llm-service/app/features/prescription/reminder_generator.py`:

```python
DEFAULT_TIME_SLOTS = {
    "morning": "08:00",    # Change to your preferred time
    "noon": "12:00",
    "afternoon": "18:00",
    "evening": "20:00",
    "night": "21:00"
}
```

## 🧪 Testing

Run the test script:
```bash
cd /home/rayu/DasTern
python3 test_reminder_generator.py
```

Expected output:
```
🎉 ALL TESTS PASSED!
✅ Generated 10 reminders for 4 medications
✅ Time slot mapping works correctly
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `ai-llm-service/app/features/prescription/reminder_generator.py` | Core reminder generation logic |
| `ai-llm-service/app/main.py` | AI service with new endpoint |
| `backend-nextjs/app/api/prescriptions/upload/route.ts` | Backend integration |
| `test_reminder_generator.py` | Test script |
| `IMPLEMENTATION_SUMMARY.md` | Full documentation |

## 🎯 Next Steps

1. ✅ **Test with Real Images**: Upload actual prescription photos
2. 🔜 **Mobile App**: Connect Flutter app to backend
3. 🔜 **Push Notifications**: Implement Firebase/OneSignal
4. 🔜 **Drug Database**: Add medication validation
5. 🔜 **Adherence Tracking**: Log taken/missed doses

## 🐛 Troubleshooting

### Issue: AI Service not responding
**Solution**: Check if Ollama is running
```bash
docker ps | grep ollama
```

### Issue: OCR not detecting Khmer text
**Solution**: Verify Tesseract has Khmer language pack
```bash
tesseract --list-langs | grep khm
```

### Issue: No reminders generated
**Solution**: Check AI service logs
```bash
docker logs ai-llm-service
```

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review test output: `test_reminder_output.json`
3. Read full docs: `IMPLEMENTATION_SUMMARY.md`

---

**🎉 Your prescription-to-reminder system is ready to use!**
