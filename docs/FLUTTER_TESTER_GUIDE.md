# 🚀 DasTern OCR + AI Tester - Quick Start Guide

## ✅ File Structure
The Flutter app is now organized with a clean, standard structure:

```
lib/main.dart
├── MODELS (Lines 1-60)
│   ├── OcrResult
│   ├── AiResult
│   └── Medication
│
├── SERVICES (Lines 65-250)
│   ├── OcrService (processImage, _extractRawText)
│   └── AiService (enhance, _extractMedications)
│
├── MAIN APP (Lines 255-275)
│   └── DasTernApp (theme, routing)
│
├── MAIN PAGE (Lines 280-450)
│   └── TestPage (state management, callbacks)
│
├── TABS (Lines 455-620)
│   ├── _ConfigTab (service URLs, settings)
│   ├── _OcrTab (image pick, OCR run)
│   └── _AiTab (AI enhance, results display)
│
└── REUSABLE WIDGETS (Lines 625-950)
    ├── _TextField, _SettingsCard, _TipsCard
    ├── _ImageCard, _PerfCard, _ErrorCard
    ├── _MedsCard, _MedItem, _MedRow
    ├── _MetricsRow, _MetricCard
    └── _JsonCard
```

## 🎯 Running the Services

### Terminal 1: Start OCR Service (Port 8000)
```bash
cd /home/rayu/DasTern/ocr-service-anti
source ../.venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
✓ Service runs on: http://localhost:8000

### Terminal 2: Start AI Service (Port 8001)
```bash
cd /home/rayu/DasTern/ai-llm-service
source ../.venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
✓ Service runs on: http://localhost:8001

### Terminal 3: Run Flutter App
```bash
cd /home/rayu/DasTern/ocr_ai_for_reminder
flutter pub get
flutter run
```
Select your phone device from the list.

## 📱 Using the Flutter App

### Tab 1: Configuration
- **OCR Base URL**: `http://10.0.2.2:8000` (emulator) or `http://<YOUR_PC_IP>:8000` (phone)
- **AI Base URL**: `http://10.0.2.2:8001` (emulator) or `http://<YOUR_PC_IP>:8001` (phone)
- **Languages**: `eng+khm+fra` (supports English, Khmer, French)

### Tab 2: OCR Testing
1. Pick an image from gallery
2. Click "Run OCR"
3. View extracted text and JSON response
4. Processing time displays in milliseconds

### Tab 3: AI Enhancement
1. Click "Enhance & Generate"
2. View extracted medications with dosage, frequency, duration
3. See reminder count and confidence score
4. View full AI response JSON

## 🔍 What the App Does

**OCR Service**:
- Accepts prescription images
- Extracts text using Tesseract
- Returns structured JSON with raw text

**AI Service**:
- Receives OCR text
- Uses fast rule-based parser (no LLM timeout)
- Extracts medications, reminders, patient info
- Processes <100ms for most prescriptions

**Flutter UI**:
- 3-tab navigation (Config → OCR → AI)
- Automatic text extraction
- Real-time performance metrics
- Dark mode support
- Error handling & snackbar notifications

## 🌐 Finding Your PC IP for Phone

```bash
# Linux
hostname -I
# Example output: 192.168.1.100

# Then use: http://192.168.1.100:8000 in the Flutter app
```

## ✨ Features

✓ Clean organized file structure (models, services, widgets)  
✓ Reusable widgets for common patterns  
✓ Proper error handling with user feedback  
✓ Performance timing display  
✓ Medication extraction and display  
✓ JSON response viewer  
✓ Editable text field for manual input  
✓ Dark mode support  
✓ Responsive design

## 🎨 UI/UX Highlights

- **Performance Metrics**: Green cards show processing time
- **Error Feedback**: Red error cards with clear messages
- **Medication Display**: Blue-tinted cards with dosage/frequency/duration
- **Auto-Navigation**: Tabs switch after successful operations
- **Visual Feedback**: Snackbar notifications for success/failure
- **Compact Design**: All info visible without excessive scrolling

---

**System Status**: ✅ All components running and ready for testing!
