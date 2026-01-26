# OCR Test Interface Setup Guide

## 🎯 Purpose
This is a standalone test interface for testing OCR and prescription formatting **WITHOUT Docker** or database connections.

## 📋 Features
- ✅ Test OCR extraction locally
- ✅ View structured prescription data
- ✅ See medication reminder schedules
- ✅ No Docker required
- ✅ No database connection needed

## 🚀 Quick Start

### Option 1: Next.js Interface (Recommended for UI Testing)

```bash
# Navigate to test interface
cd ai_ocr_interface_test

# Install dependencies
npm install

# Run development server
npm run dev

# Open in browser
# http://localhost:3000/test-ocr
```

### Option 2: Python Standalone Script (For Real OCR Testing)

```bash
# Navigate to project root
cd /home/rayu/DasTern

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install OCR dependencies
pip install -r ocr-service/requirements.txt

# Run OCR test on an image
python test-ocr-standalone.py path/to/prescription.jpg

# Example output saved to: test_ocr_result.json
```

## 📁 Files Created

### 1. **test-ocr-standalone.py** (Root directory)
Standalone Python script for testing OCR without Docker.

**Usage:**
```bash
python test-ocr-standalone.py prescription_image.jpg
```

**Output:**
- Console display with formatted results
- JSON file: `test_ocr_result.json`

**Features:**
- ✅ Extracts text using PaddleOCR
- ✅ Formats data into prescription structure
- ✅ Generates reminder schedules
- ✅ Shows confidence scores

### 2. **ai_ocr_interface_test/app/test-ocr/page.tsx**
Next.js page for visual OCR testing interface.

**Features:**
- 📸 Upload prescription images
- 🔍 View OCR blocks with confidence
- 💊 Structured prescription display
- ⏰ Medication reminder schedule
- 📊 Tabs for organized viewing

### 3. **ai_ocr_interface_test/app/page.tsx**
Updated home page with links to test interface.

## 🧪 Testing Workflow

### Step 1: Prepare Test Image
Get a prescription image (JPG, PNG, etc.)

### Step 2A: Test with Python Script
```bash
source .venv/bin/activate
python test-ocr-standalone.py prescription.jpg
```

**Output shows:**
1. OCR extraction results
2. Extracted text blocks
3. Prescription formatting
4. Reminder schedule
5. Confidence scores

### Step 2B: Test with Next.js UI
```bash
cd ai_ocr_interface_test
npm run dev
```

Visit `http://localhost:3000/test-ocr` and:
1. Upload prescription image
2. Click "Process OCR"
3. View results in tabs:
   - 📝 OCR Blocks
   - 💊 Prescription Data
   - ⏰ Reminder Schedule

## 📊 Output Format

### Prescription Structure
```json
{
  "patient_info": {
    "name": "John Doe",
    "age": null,
    "gender": null,
    "patient_id": null
  },
  "prescription_details": {
    "date": "26/01/2026",
    "doctor_name": "Dr. Sarah Johnson",
    "clinic_name": "City Medical Center",
    "diagnosis": "Common Cold"
  },
  "medications": [
    {
      "name": "Amoxicillin 500mg",
      "dosage": "1 tablet",
      "frequency": "3 times daily",
      "duration": "7 days",
      "instructions": "After meals"
    }
  ],
  "dosage_instructions": [...],
  "reminder_schedule": [
    {
      "time": "08:00",
      "instruction": "Amoxicillin 500mg - 1 tablet after breakfast",
      "enabled": true
    }
  ],
  "raw_ocr_data": {
    "full_text": "...",
    "confidence": 0.90,
    "blocks_count": 14,
    "language": "en"
  }
}
```

## 🔧 Troubleshooting

### PaddlePaddle Installation Error
If you get "No matching distribution found for paddlepaddle==3.2.0":

✅ **FIXED**: Updated requirements.txt to use PaddleOCR 2.7.x which is more stable.

```bash
# Reinstall with updated requirements
pip install -r ocr-service/requirements.txt
```

### Next.js Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Image Upload Issues
- Ensure image is valid format (JPG, PNG, etc.)
- Check file size (keep under 10MB for testing)
- Verify image is readable

## 📝 Notes

### Current Testing Mode
- **Next.js UI**: Uses MOCK data for testing UI
- **Python Script**: Uses REAL PaddleOCR extraction

### To Connect Real OCR to Next.js
You would need to:
1. Start OCR service backend
2. Update Next.js API routes
3. Configure CORS settings

But for **local testing without Docker**, the mock mode works perfectly!

## 🎨 Reminder Format Examples

The system generates reminders based on detected timing keywords:

| Text Detected | Generated Reminders |
|--------------|---------------------|
| "3 times daily after meals" | 08:00, 14:00, 20:00 |
| "twice a day" | 09:00, 21:00 |
| "morning and night" | 08:00, 21:00 |
| "as needed" | No fixed schedule |

## ✅ Success Indicators

When testing is successful, you should see:
- ✅ OCR confidence > 70%
- ✅ Medications extracted correctly
- ✅ Reminder times generated
- ✅ Dosage instructions formatted
- ✅ JSON output saved

## 🚫 What's NOT Tested

This standalone testing does NOT include:
- ❌ Database storage
- ❌ User authentication
- ❌ API endpoints
- ❌ Docker containers
- ❌ Production deployment

This is purely for **OCR extraction and formatting validation**.

## 📞 Need Help?

Check the console output for detailed error messages and stack traces.
