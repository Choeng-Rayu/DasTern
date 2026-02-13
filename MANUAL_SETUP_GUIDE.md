# Manual Setup & Usage Guide (Step-by-Step)

**For: DasTern Prescription Processing System**

This guide shows you how to manually start and use each service without using the automated `start_all_services.sh` script. Perfect for understanding how everything works or for development.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Part 1: Installation & Setup (First Time Only)](#part-1-installation--setup-first-time-only)
3. [Part 2: Opening VSCode & Starting Services](#part-2-opening-vscode--starting-services)
4. [Part 3: Using the System to Extract & Organize Data](#part-3-using-the-system-to-extract--organize-data)
5. [Part 4: Working with the Data](#part-4-working-with-the-data)
6. [Part 5: Troubleshooting](#part-5-troubleshooting)
7. [Part 6: Stopping Services](#part-6-stopping-services)
8. [Appendix](#appendix)

---

## Prerequisites

Before starting, ensure you have:
- **VSCode** installed
- **Python 3.10 or higher** (`python3 --version`)
- **Flutter SDK** installed and in PATH (`flutter --version`)
- **Homebrew** (macOS) or your system's package manager
- **Terminal** knowledge (basic commands like `cd`, `ls`)

---

## Part 1: Installation & Setup (First Time Only)

### 1.1: Install System Dependencies

#### Install Tesseract OCR (Required for text extraction)

```bash
# macOS
brew install tesseract

# Install additional language packs for multilingual support
brew install tesseract-lang

# Verify installation
tesseract --version
# Should show: tesseract 5.x.x

# Check available languages
tesseract --list-langs
# Should include: eng, fra, khm (English, French, Khmer)
```

**Why?** Tesseract is the OCR engine that extracts text from prescription images.

#### Install Ollama (Required for AI processing)

```bash
# macOS
brew install ollama

# Verify installation
ollama --version
```

#### Download the AI Model (One-time, ~2GB download)

```bash
# Start Ollama (in a terminal)
ollama serve

# In a NEW terminal, download the model
ollama pull llama3.2:3b

# Verify model is downloaded
ollama list
# Should show: llama3.2:3b
```

**Why?** Ollama runs the AI model locally that corrects OCR errors and extracts medication schedules.

---

### 1.2: Setup Python Virtual Environments

#### For OCR Service

```bash
# Navigate to OCR service folder
cd /Users/macbook/CADT/DasTern/ocr-service-anti

# Create virtual environment (first time only)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your terminal prompt should now show (venv) at the beginning

# Install dependencies
pip install -r requirements.txt

# Wait for installation to complete (may take a few minutes)

# Deactivate when done
deactivate
```

**Why?** Virtual environments isolate Python dependencies for each project.

#### For AI-LLM Service

```bash
# Navigate to AI service folder
cd /Users/macbook/CADT/DasTern/ai-llm-service

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

---

### 1.3: Setup Flutter App

```bash
# Navigate to Flutter app folder
cd /Users/macbook/CADT/DasTern/ocr_ai_for_reminder

# Get Flutter dependencies
flutter pub get

# This downloads all required packages
# Wait for "Got dependencies!" message
```

**Configuration Check:**

The Flutter app should already be configured to connect to `http://127.0.0.1:8000` (OCR) and `http://127.0.0.1:8001` (AI). You can verify this in:

```
ocr_ai_for_reminder/lib/core/constants/api_constants.dart
```

---

## Part 2: Opening VSCode & Starting Services

### 2.1: Open VSCode

1. Launch VSCode
2. Open the DasTern folder:
   - `File` → `Open Folder...`
   - Navigate to `/Users/macbook/CADT/DasTern`
   - Click `Open`

3. Open the integrated terminal:
   - Press `` Ctrl+` `` (backtick) or
   - `Terminal` → `New Terminal`

4. Split the terminal into 4 panes:
   - Click the split icon (📱) in terminal panel
   - Repeat 3 times to get 4 terminal panes

You should now have 4 terminals ready. Label them mentally:
- **Terminal 1**: Ollama
- **Terminal 2**: OCR Service
- **Terminal 3**: AI Service
- **Terminal 4**: Flutter App

---

### 2.2: Start Ollama (Terminal 1)

**Why?** The AI service needs Ollama running to function. Start this FIRST.

```bash
# In Terminal 1
ollama serve
```

**Expected Output:**
```
Listening on 127.0.0.1:11434
```

**Verify it's running** (open a new terminal temporarily):
```bash
curl http://localhost:11434/api/tags
```

**Expected Response:**
```json
{
  "models": [
    {
      "name": "llama3.2:3b",
      ...
    }
  ]
}
```

✅ **Keep this terminal running!** Don't close it or press Ctrl+C.

---

### 2.3: Start OCR Service (Terminal 2)

**Why?** This service extracts text from prescription images using Tesseract.

```bash
# In Terminal 2
cd /Users/macbook/CADT/DasTern/ocr-service-anti

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)

# Start the OCR service on port 8000
python main.py 8000
```

**Expected Output:**
```
🚀 Starting OCR Service on http://127.0.0.1:8000
📚 API Documentation: http://127.0.0.1:8000/docs
INFO:     Started server process [XXXXX]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Verify it's healthy** (open a new terminal temporarily):
```bash
curl http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "ocr-service",
  "version": "1.0.0"
}
```

✅ **Keep this terminal running!**

**API Documentation:** Open http://127.0.0.1:8000/docs in your browser to see all available endpoints.

---

### 2.4: Start AI-LLM Service (Terminal 3)

**Why?** This service corrects OCR errors and extracts structured medication data using AI.

```bash
# In Terminal 3
cd /Users/macbook/CADT/DasTern/ai-llm-service

# Activate virtual environment
source venv/bin/activate

# Set Ollama endpoint (important!)
export OLLAMA_HOST=http://localhost:11434

# Start the AI service
python app/main_ollama.py
```

**Expected Output:**
```
INFO:     Started server process [XXXXX]
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Ollama endpoint: http://localhost:11434
INFO:     Default model (3B): llama3.2:3b
```

**Verify it's healthy** (open a new terminal temporarily):
```bash
curl http://127.0.0.1:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "ollama-ai-service",
  "ollama_connected": true
}
```

✅ **Keep this terminal running!**

---

### 2.5: Start Flutter Interface (Terminal 4)

**Why?** This is your user interface for the entire system.

```bash
# In Terminal 4
cd /Users/macbook/CADT/DasTern/ocr_ai_for_reminder

# Run the Flutter app on macOS
flutter run -d macos
```

**Expected Output:**
```
Launching lib/main.dart on macOS in debug mode...
Building macOS application...
✓ Built build/macos/Build/Products/Debug/Runner.app

A Dart VM Service is available at: http://127.0.0.1:XXXXX
The Flutter DevTools debugger is available at: http://...
```

**The app window should open automatically.**

✅ If the app opens successfully, all services are ready!

---

## Part 3: Using the System to Extract & Organize Data

### 3.1: Extract Data from Prescription Image (OCR Service)

You can extract data in two ways:

#### Method 1: Using Flutter Interface (Recommended for Users)

1. **In the Flutter app**, click **"Upload Prescription"** or **"Take Photo"**
2. **Select an image file** (JPG, PNG) of a prescription
3. **Watch the processing status**:
   - "Reading prescription..." (OCR running)
   - "Understanding prescription..." (AI processing)
4. **View the extracted text** in the results screen
5. **See the organized medication list** below

**What happens behind the scenes:**
- Image is sent to OCR Service (port 8000)
- OCR extracts text and returns JSON
- Text is sent to AI Service (port 8001)
- AI corrects errors and extracts medications
- Results are displayed in the app

---

#### Method 2: Using curl (For Testing/Understanding)

This shows you exactly what the Flutter app does.

**Step 1: Prepare a prescription image**
```bash
# Use any prescription image you have, for example:
# /Users/macbook/Pictures/prescription_sample.jpg
```

**Step 2: Send image to OCR service**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ocr" \
  -F "file=@/Users/macbook/Pictures/prescription_sample.jpg"
```

**Expected Response (simplified):**
```json
{
  "success": true,
  "full_text": "Paracetamol 500mg\nTake 2 tablets 3 times daily\nDuration: 5 days",
  "words": [
    {
      "text": "Paracetamol",
      "x": 120,
      "y": 45,
      "width": 180,
      "height": 30,
      "confidence": 0.95
    },
    {
      "text": "500mg",
      "x": 310,
      "y": 45,
      "width": 90,
      "height": 30,
      "confidence": 0.92
    }
  ],
  "quality_metrics": {
    "blur_score": 150.5,
    "contrast_score": 85.2,
    "dpi": 300
  }
}
```

**Understanding the Response:**
- `full_text`: Complete extracted text
- `words`: Array of individual words with positions
  - `x, y`: Position in image (pixels from top-left)
  - `width, height`: Size of word
  - `confidence`: AI's confidence in this word (0-1)
- `quality_metrics`: Image quality assessment
  - Higher `blur_score` = sharper image
  - DPI = dots per inch (300+ is good)

---

### 3.2: Organize Data with AI-LLM Service

#### Automatic Flow (via Flutter App)

When you use the Flutter app, the AI processing happens automatically:

1. OCR text is extracted
2. **Automatically sent to AI service**
3. AI corrects OCR errors (e.g., "5OOmg" → "500mg")
4. AI extracts medication information:
   - Medication names
   - Dosages
   - Timing schedules
   - Duration
   - Special instructions
5. **Converts vague times to specific hours:**
   - "3 times daily" → 08:00, 12:00, 18:00
   - "twice daily" → 08:00, 20:00
   - "once at bedtime" → 21:00
6. Results displayed in app

---

#### Manual Flow (Understanding the Process with curl)

**Step 1: Take OCR output from previous step**

Let's say the OCR returned:
```
"full_text": "Paracetam0l 50Omg\nTake 2 tab1ets 3 times dai1y\nDuration: 5 days"
```

Notice the errors: `0` instead of `o`, `O` instead of `0`, `1` instead of `l`

**Step 2: Send to AI for error correction**

```bash
curl -X POST "http://127.0.0.1:8001/correct-ocr" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Paracetam0l 50Omg\nTake 2 tab1ets 3 times dai1y",
    "language": "en"
  }'
```

**Expected Response:**
```json
{
  "corrected_text": "Paracetamol 500mg\nTake 2 tablets 3 times daily",
  "confidence": 0.85,
  "corrections_made": 4,
  "model_used": "llama3.2:3b"
}
```

**Step 3: Send to AI for medication extraction**

```bash
curl -X POST "http://127.0.0.1:8001/extract-reminders" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_ocr_json": {
      "full_text": "Paracetamol 500mg\nTake 2 tablets 3 times daily\nDuration: 5 days"
    }
  }'
```

**Expected Response:**
```json
{
  "medications": [
    {
      "name": "Paracetamol",
      "dosage": "500mg",
      "times": ["morning", "noon", "evening"],
      "times_24h": ["08:00", "12:00", "18:00"],
      "repeat": "daily",
      "duration_days": 5,
      "notes": "Take 2 tablets 3 times daily"
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

---

### 3.3: Understanding the Data Flow

```
┌─────────────────────┐
│ Prescription Image  │
│  (JPG/PNG file)     │
└──────────┬──────────┘
           │
           │ 1. Upload via Flutter
           ↓
┌─────────────────────┐
│    Flutter App      │
│  (User Interface)   │
└──────────┬──────────┘
           │
           │ 2. HTTP POST to port 8000
           ↓
┌─────────────────────────────────────────┐
│         OCR Service (Port 8000)         │
│                                         │
│  1. Validates image (size, format)      │
│  2. Analyzes quality (blur, contrast)   │
│  3. Enhances image (de-skew, sharpen)   │
│  4. Extracts text with Tesseract        │
│  5. Returns JSON with text + positions  │
└──────────┬──────────────────────────────┘
           │
           │ 3. Returns JSON response
           │    {
           │      "full_text": "...",
           │      "words": [...],
           │      "confidence": 0.95
           │    }
           ↓
┌─────────────────────┐
│    Flutter App      │
│ (Receives OCR data) │
└──────────┬──────────┘
           │
           │ 4. HTTP POST to port 8001
           │    with extracted text
           ↓
┌─────────────────────────────────────────┐
│       AI-LLM Service (Port 8001)        │
│         (Uses Ollama + llama3.2:3b)     │
│                                         │
│  1. Corrects OCR errors                 │
│     "Paracetam0l" → "Paracetamol"      │
│  2. Extracts medication names           │
│  3. Identifies dosages                  │
│  4. Parses timing instructions          │
│     "3 times daily" → 08:00,12:00,18:00│
│  5. Extracts duration                   │
│  6. Preserves special notes             │
│  7. Returns structured JSON             │
└──────────┬──────────────────────────────┘
           │
           │ 5. Returns organized data
           │    {
           │      "medications": [
           │        {
           │          "name": "Paracetamol",
           │          "times_24h": ["08:00","12:00","18:00"],
           │          ...
           │        }
           │      ]
           │    }
           ↓
┌─────────────────────┐
│    Flutter App      │
│  (Shows Results)    │
│                     │
│  📋 Medications:    │
│  • Paracetamol      │
│    500mg            │
│    ⏰ 08:00         │
│    ⏰ 12:00         │
│    ⏰ 18:00         │
└─────────────────────┘
```

**Key Points:**
- Each service has a specific job
- Services communicate via HTTP/REST APIs
- Flutter app orchestrates the workflow
- All processing happens locally (no cloud)
- Data flows in one direction: Image → Text → Structured Data

---

## Part 4: Working with the Data

### 4.1: OCR Output Format

When you call the OCR service, you get JSON like this:

```json
{
  "success": true,
  "full_text": "Paracetamol 500mg\nTake 2 tablets 3 times daily",
  "words": [
    {
      "text": "Paracetamol",
      "x": 120,
      "y": 45,
      "width": 180,
      "height": 30,
      "confidence": 0.95
    }
  ],
  "lines": [
    {
      "text": "Paracetamol 500mg",
      "words": [...],
      "confidence": 0.93
    }
  ],
  "quality_metrics": {
    "blur_score": 150.5,
    "contrast_score": 85.2,
    "dpi": 300,
    "recommendations": []
  },
  "filename": "prescription.jpg",
  "timestamp": "2026-02-12T10:30:00",
  "processing_time_ms": 1245
}
```

**Field Explanations:**
- `full_text`: All extracted text concatenated
- `words`: Array of individual words with bounding boxes
  - Useful for highlighting text in UI
  - Can show confidence scores for each word
- `lines`: Text grouped by lines
- `quality_metrics`: Image quality assessment
  - `blur_score`: Higher = sharper (>100 is good)
  - `contrast_score`: 30-200 range (too low or high is bad)
  - `dpi`: Resolution (300+ is ideal)
  - `recommendations`: Suggests improvements if needed
- `processing_time_ms`: How long OCR took

**Using the Data:**
```dart
// In Flutter
final response = await ocrService.processImage(imagePath);
final text = response.fullText;
final confidence = response.words.first.confidence;

// Show bounding boxes in UI
for (var word in response.words) {
  drawBox(x: word.x, y: word.y, width: word.width, height: word.height);
}
```

---

### 4.2: AI-Organized Data Format

When you call the AI service, you get structured medication data:

```json
{
  "medications": [
    {
      "name": "Paracetamol",
      "dosage": "500mg",
      "times": ["morning", "noon", "evening"],
      "times_24h": ["08:00", "12:00", "18:00"],
      "repeat": "daily",
      "duration_days": 5,
      "notes": "Take 2 tablets 3 times daily with food"
    },
    {
      "name": "Amoxicillin",
      "dosage": "250mg",
      "times": ["morning", "evening"],
      "times_24h": ["08:00", "20:00"],
      "repeat": "daily",
      "duration_days": 7,
      "notes": "Take with meals"
    }
  ],
  "success": true,
  "error": null,
  "metadata": {
    "model": "llama3.2:3b",
    "attempts": 1,
    "processing_time_ms": 2340
  }
}
```

**Field Explanations:**
- `medications`: Array of all medications found
  - `name`: Medication name (e.g., "Paracetamol")
  - `dosage`: Strength (e.g., "500mg")
  - `times`: Human-readable times (e.g., ["morning", "noon"])
  - `times_24h`: Specific times in 24-hour format (e.g., ["08:00", "12:00"])
    - These can be used to set phone reminders
  - `repeat`: Frequency ("daily", "as_needed", "weekly")
  - `duration_days`: How many days to take (null if long-term)
  - `notes`: Original instructions + any special warnings

**Time Conversion Logic:**
- "once daily" → ["08:00"]
- "twice daily" → ["08:00", "20:00"]
- "3 times daily" → ["08:00", "12:00", "18:00"]
- "4 times daily" → ["08:00", "12:00", "16:00", "20:00"]
- "at bedtime" → ["21:00"]
- "with breakfast" → ["08:00"]

**Using the Data:**
```dart
// In Flutter
final response = await aiService.extractReminders(ocrData);

for (var med in response.medications) {
  // Create reminders in calendar
  for (var time in med.times24h) {
    setReminder(
      title: '${med.name} ${med.dosage}',
      time: time,
      repeatDaily: med.repeat == 'daily',
      duration: med.durationDays,
    );
  }

  // Display in UI
  showMedicationCard(
    name: med.name,
    dosage: med.dosage,
    schedule: med.times24h,
    notes: med.notes,
  );
}
```

---

### 4.3: Using the Data

**What you can do with the organized data:**

1. **Set Phone Reminders**
   ```dart
   // Use times_24h array
   for (var medication in medications) {
     for (var time in medication.times_24h) {
       scheduleNotification(
         title: 'Take ${medication.name}',
         time: time,
       );
     }
   }
   ```

2. **Export to Calendar**
   ```dart
   // Create calendar events
   createCalendarEvents(
     title: 'Medication: ${medication.name}',
     times: medication.times_24h,
     duration: medication.duration_days,
   );
   ```

3. **Save to Database** (Future Enhancement)
   ```dart
   // Store in local database
   await database.insert('prescriptions', {
     'medication_name': medication.name,
     'dosage': medication.dosage,
     'schedule': jsonEncode(medication.times_24h),
     'start_date': DateTime.now(),
     'end_date': DateTime.now().add(
       Duration(days: medication.duration_days!)
     ),
   });
   ```

4. **Print Summary**
   ```dart
   printPDFSummary(
     'Your Medication Schedule',
     medications: medications,
   );
   ```

5. **Share with Doctor**
   ```dart
   shareText(
     'Prescription Details:\n' +
     medications.map((m) =>
       '${m.name} ${m.dosage}\n' +
       'Times: ${m.times_24h.join(", ")}\n' +
       'Duration: ${m.duration_days} days'
     ).join('\n\n')
   );
   ```

---

## Part 5: Troubleshooting

### Common Issues

#### Issue 1: Service Won't Start - "Address already in use"

**Error Message:**
```
ERROR:    [Errno 48] Address already in use
```

**Cause:** Port 8000 or 8001 is already in use by another process.

**Solution:**
```bash
# Find what's using the port
lsof -i :8000  # For OCR service
lsof -i :8001  # For AI service

# Kill the process (replace PID with actual number)
kill <PID>

# Or kill all Python processes
pkill -f "python.*main"

# Now try starting the service again
```

---

#### Issue 2: "Connection refused" in Flutter App

**Error Message:**
```
Exception: Connection refused (http://127.0.0.1:8000)
```

**Cause:** OCR or AI service is not running.

**Solution:**
```bash
# Check if services are running
curl http://127.0.0.1:8000/health  # OCR
curl http://127.0.0.1:8001/health  # AI

# If they fail, start the services:
# See Part 2.3 and 2.4
```

---

#### Issue 3: "Tesseract not found"

**Error Message:**
```
TesseractNotFoundError: Tesseract not found at /opt/homebrew/bin/tesseract
```

**Cause:** Tesseract is not installed or not in the expected location.

**Solution:**
```bash
# Check if Tesseract is installed
tesseract --version

# If not installed:
brew install tesseract tesseract-lang

# Find where it's installed
which tesseract

# If it's in a different location, update the config:
# Edit: ocr-service-anti/app/core/config.py
# Change tesseract_cmd to the path from 'which tesseract'
```

---

#### Issue 4: "ollama_connected: false"

**Error Message (in AI service):**
```json
{
  "status": "degraded",
  "ollama_connected": false
}
```

**Cause:** Ollama is not running.

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If it fails, start Ollama:
ollama serve

# In another terminal, verify:
ollama list
# Should show: llama3.2:3b
```

---

#### Issue 5: "Model not found"

**Error Message:**
```
Error: model 'llama3.2:3b' not found
```

**Cause:** Model hasn't been downloaded.

**Solution:**
```bash
# Download the model (one-time, ~2GB)
ollama pull llama3.2:3b

# Verify it's downloaded
ollama list

# Should show:
# NAME              ID              SIZE
# llama3.2:3b       a80c4f17acd5    2.0 GB
```

---

#### Issue 6: Flutter App Can't Load

**Error:** App crashes or shows blank screen.

**Solution:**
```bash
# Check Flutter doctor
flutter doctor

# Clean and rebuild
cd ocr_ai_for_reminder
flutter clean
flutter pub get
flutter run -d macos
```

---

### Verification Commands

Use these to check if everything is working:

```bash
# 1. Check Ollama
curl http://localhost:11434/api/tags
# Expected: JSON with models array

# 2. Check OCR Service
curl http://127.0.0.1:8000/health
# Expected: {"status": "healthy", ...}

# 3. Check OCR with Tesseract
curl -s http://127.0.0.1:8000/api/v1/health | grep tesseract_available
# Expected: "tesseract_available": true

# 4. Check AI Service
curl http://127.0.0.1:8001/health
# Expected: {"status": "healthy", "ollama_connected": true}

# 5. Check all ports
lsof -i :8000   # OCR Service
lsof -i :8001   # AI Service
lsof -i :11434  # Ollama
# Each should show a running process

# 6. Test OCR correction
curl -X POST http://127.0.0.1:8001/correct-ocr \
  -H "Content-Type: application/json" \
  -d '{"text":"helo wrold","language":"en"}'
# Expected: JSON with corrected text
```

---

### Viewing Logs

#### OCR Service Logs
```bash
# If started with start_all_services.sh:
tail -f /tmp/ocr_service.log

# If started manually in terminal:
# Logs appear directly in the terminal where you ran it
```

#### AI Service Logs
```bash
# If started with start_all_services.sh:
tail -f /tmp/ai_service.log

# If started manually:
# Logs appear in the terminal
```

#### Flutter App Logs
```bash
# In the terminal where you ran flutter run
# Logs appear automatically

# Or in a separate terminal:
flutter logs
```

---

## Part 6: Stopping Services

### Properly Stopping Each Service

```bash
# 1. Stop Flutter App
# In the Flutter terminal, press:
q  # (just the letter q)

# Or press:
Ctrl+C

# 2. Stop AI Service
# In the AI service terminal, press:
Ctrl+C

# 3. Stop OCR Service
# In the OCR service terminal, press:
Ctrl+C

# 4. Stop Ollama
# In the Ollama terminal, press:
Ctrl+C
```

### Forcefully Kill Services (if needed)

```bash
# Kill by port
kill $(lsof -t -i :8000)  # OCR Service
kill $(lsof -t -i :8001)  # AI Service
kill $(lsof -t -i :11434) # Ollama

# Or kill all Python services
pkill -f "python.*main"
pkill -f "uvicorn"

# Kill Ollama
pkill ollama
```

### Verify Everything is Stopped

```bash
# Check ports (should return nothing)
lsof -i :8000
lsof -i :8001
lsof -i :11434

# If empty, everything is stopped ✅
```

---

## Appendix

### A. Service Ports Reference

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| OCR Service | 8000 | http://127.0.0.1:8000 | Extract text from images |
| AI Service | 8001 | http://127.0.0.1:8001 | Correct errors & extract medications |
| Ollama | 11434 | http://localhost:11434 | Run AI model (llama3.2:3b) |
| Flutter App | N/A | Desktop app | User interface |

---

### B. Important File Paths

| Component | File | Purpose |
|-----------|------|---------|
| OCR Config | `ocr-service-anti/app/core/config.py` | Tesseract settings, languages |
| AI Config | `ai-llm-service/app/core/config.py` | Ollama endpoint, model name |
| Flutter API | `ocr_ai_for_reminder/lib/core/constants/api_constants.dart` | Service URLs |
| OCR Main | `ocr-service-anti/main.py` | Start OCR service |
| AI Main | `ai-llm-service/app/main_ollama.py` | Start AI service |

---

### C. Sample curl Commands

#### Test OCR Service

```bash
# Health check
curl http://127.0.0.1:8000/health

# Detailed health (with Tesseract info)
curl http://127.0.0.1:8000/api/v1/health

# Process an image
curl -X POST "http://127.0.0.1:8000/api/v1/ocr" \
  -F "file=@/path/to/prescription.jpg"
```

#### Test AI Service

```bash
# Health check
curl http://127.0.0.1:8001/health

# Correct OCR errors
curl -X POST "http://127.0.0.1:8001/correct-ocr" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Paracetam0l 50Omg take 2 tab1ets",
    "language": "en"
  }'

# Extract medication reminders
curl -X POST "http://127.0.0.1:8001/extract-reminders" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_ocr_json": {
      "full_text": "Paracetamol 500mg\nTake 3 times daily for 5 days"
    }
  }'
```

#### Test Ollama

```bash
# List models
curl http://localhost:11434/api/tags

# Generate text (direct Ollama call)
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "prompt": "Extract medication: Paracetamol 500mg BD",
    "stream": false
  }'
```

---

### D. Understanding Virtual Environments

**Why use virtual environments?**
- Isolates Python packages for each project
- Prevents dependency conflicts
- Easier to reproduce exact environment

**How to activate/deactivate:**
```bash
# Activate
source venv/bin/activate
# Prompt changes to: (venv) user@computer:~$

# Deactivate
deactivate
# Prompt returns to: user@computer:~$
```

**Where are packages installed?**
```bash
# When venv is active, packages go here:
ocr-service-anti/venv/lib/python3.x/site-packages/
ai-llm-service/venv/lib/python3.x/site-packages/

# NOT in system Python
```

**To see installed packages:**
```bash
source venv/bin/activate
pip list
```

---

## Summary

**To use the system after initial setup:**

1. **Open VSCode** with 4 terminal panes
2. **Terminal 1:** `ollama serve`
3. **Terminal 2:**
   ```bash
   cd ocr-service-anti
   source venv/bin/activate
   python main.py 8000
   ```
4. **Terminal 3:**
   ```bash
   cd ai-llm-service
   source venv/bin/activate
   export OLLAMA_HOST=http://localhost:11434
   python app/main_ollama.py
   ```
5. **Terminal 4:**
   ```bash
   cd ocr_ai_for_reminder
   flutter run -d macos
   ```

6. **Upload prescription image** in the Flutter app
7. **View extracted and organized data**

**To stop:** Press `Ctrl+C` in each terminal (or `q` in Flutter terminal)

---

**Need help?** Check the [Troubleshooting](#part-5-troubleshooting) section or run the automated test script:
```bash
cd /Users/macbook/CADT/DasTern
./test_demo.sh
```

**For automated startup,** use:
```bash
./start_all_services.sh
```
