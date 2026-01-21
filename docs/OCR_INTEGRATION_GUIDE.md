# 🚀 DasTern OCR Integration - Complete Guide

## 📋 What's Been Implemented

### ✅ Backend (Next.js)
- **PostgreSQL Database Connection** (`lib/db.ts`)
- **TypeScript Types** matching database schema (`lib/types.ts`)
- **API Routes**:
  - `POST /api/prescriptions/upload` - Upload and process prescription images
  - `POST /api/reminders/create` - Create medication reminders
  - `GET /api/reminders/create?patient_id=xxx` - Fetch patient reminders
  - `GET /api/health` - Health check for all services
- **Web Interface** (`app/page.tsx`) - OCR testing UI with drag & drop

### ✅ OCR Service (Enhanced)
- Added `POST /process` endpoint for backend integration
- Returns standardized format: `raw_text`, `confidence`, `language`
- Supports multi-language: English, Khmer, French

### ✅ AI Service (Enhanced)
- Added `POST /correct-ocr` endpoint for OCR enhancement
- Accepts JSON: `{"text": "...", "language": "en"}`
- Returns corrected text with confidence scores

---

## 🔧 Setup & Installation

### Step 1: Install Dependencies

```bash
cd ~/DasTern/backend-nextjs

# Install new packages
docker compose exec backend npm install

# Or if not running, rebuild
docker compose build backend
```

### Step 2: Start All Services

```bash
cd ~/DasTern

# Start everything
./docker-start.sh

# Or manually
docker compose up -d
```

### Step 3: Verify Services

```bash
# Check all services are running
docker compose ps

# Should show:
# ✅ dastern-postgres (healthy)
# ✅ dastern-backend (running)
# ✅ dastern-ocr (running)
# ✅ dastern-ai (running)
```

---

## 🧪 Testing the OCR System

### Test 1: Health Check

```bash
# Check backend health
curl http://localhost:3000/api/health

# Expected output:
{
  "status": "healthy",
  "timestamp": "2026-01-21...",
  "database": "connected",
  "services": {
    "ocr": "available",
    "ai": "available"
  }
}
```

### Test 2: Database Connection

```bash
# Connect to database
docker compose exec postgres psql -U dastern -d dastern

# Check tables
\dt

# Should see:
# - users
# - prescriptions
# - medications
# - medication_reminders
# ... and 16 more tables

\q
```

### Test 3: OCR Service Direct Test

```bash
# Test OCR service directly
curl -X POST http://localhost:8000/health

# Upload a test image
curl -X POST http://localhost:8000/process \
  -F "file=@/path/to/prescription.jpg"

# Expected:
{
  "raw_text": "Amoxicillin 500mg...",
  "confidence": 0.95,
  "language": "eng"
}
```

### Test 4: AI Service Direct Test

```bash
# Test AI service
curl http://localhost:8001/health

# Test OCR correction
curl -X POST http://localhost:8001/correct-ocr \
  -H "Content-Type: application/json" \
  -d '{"text": "Amxicillin 500mg", "language": "en"}'

# Expected:
{
  "corrected_text": "Amoxicillin 500mg",
  "confidence": 0.98,
  "corrections_made": 1
}
```

### Test 5: Full Integration Test (Web Interface)

1. **Open Browser**: http://localhost:3000
2. **Upload Image**: Drag & drop or click to select prescription image
3. **Process**: Click "🚀 Process Prescription" button
4. **View Results**:
   - Extracted text with confidence score
   - AI enhancement status (🤖 AI Enhanced or 📝 OCR Only)
   - List of detected medications
   - Prescription ID

---

## 📊 API Documentation

### Upload Prescription

**Endpoint**: `POST /api/prescriptions/upload`

**Request**:
```bash
curl -X POST http://localhost:3000/api/prescriptions/upload \
  -F "image=@prescription.jpg" \
  -F "patient_id=00000000-0000-0000-0000-000000000000"
```

**Response**:
```json
{
  "success": true,
  "prescription_id": "uuid-here",
  "ocr_text": "Extracted prescription text...",
  "ocr_confidence": 0.95,
  "ai_enhanced": true,
  "medications": [
    {
      "name": "Amoxicillin",
      "strength": "500mg",
      "dosage": "1 tablet",
      "frequency": "twice daily",
      "duration": "for 7 days"
    }
  ],
  "message": "Prescription processed successfully"
}
```

### Create Reminder

**Endpoint**: `POST /api/reminders/create`

**Request**:
```bash
curl -X POST http://localhost:3000/api/reminders/create \
  -H "Content-Type: application/json" \
  -d '{
    "medication_id": "uuid-here",
    "patient_id": "uuid-here",
    "reminder_times": ["08:00", "20:00"],
    "start_date": "2026-01-21",
    "end_date": "2026-01-28",
    "days_of_week": [1,2,3,4,5,6,7]
  }'
```

**Response**:
```json
{
  "success": true,
  "reminder_id": "uuid-here",
  "medication": {
    "name": "Amoxicillin",
    "dosage": "1 tablet",
    "frequency": "twice daily"
  },
  "reminder_times": ["08:00", "20:00"],
  "start_date": "2026-01-21",
  "message": "Reminder created successfully"
}
```

### Get Reminders

**Endpoint**: `GET /api/reminders/create?patient_id={id}`

**Request**:
```bash
curl http://localhost:3000/api/reminders/create?patient_id=00000000-0000-0000-0000-000000000000
```

**Response**:
```json
{
  "success": true,
  "reminders": [
    {
      "reminder_id": "uuid",
      "reminder_times": ["08:00", "20:00"],
      "start_date": "2026-01-21",
      "medication_name": "Amoxicillin",
      "dosage": "1 tablet",
      "frequency": "twice daily"
    }
  ]
}
```

---

## 🔍 Database Schema Verification

The system follows the database format defined in `database/schema.sql`:

### Prescriptions Table
```sql
prescriptions (
  id UUID PRIMARY KEY,
  patient_id UUID REFERENCES users(id),
  original_image_url VARCHAR,
  ocr_raw_text TEXT,
  ocr_corrected_text TEXT,
  ocr_confidence_score DECIMAL(5,4),
  ai_confidence_score DECIMAL(5,4),
  status prescription_status,
  ...
)
```

### Medications Table
```sql
medications (
  id UUID PRIMARY KEY,
  prescription_id UUID REFERENCES prescriptions(id),
  name VARCHAR(200),
  strength VARCHAR(100),
  dosage VARCHAR(200),
  frequency VARCHAR(100),
  duration VARCHAR(100),
  ...
)
```

### Medication Reminders Table
```sql
medication_reminders (
  id UUID PRIMARY KEY,
  medication_id UUID REFERENCES medications(id),
  patient_id UUID REFERENCES users(id),
  reminder_times TIME[],
  start_date DATE,
  end_date DATE,
  is_active BOOLEAN,
  ...
)
```

**✅ All API routes save data in the correct database format!**

---

## 🔄 Development Workflow

### Modify Code & Test

**Backend Changes (Next.js)**:
1. Edit file: `backend-nextjs/app/...`
2. Save (Ctrl+S)
3. **Auto-reloads!** Refresh browser to see changes
4. View logs: `docker compose logs -f backend`

**OCR Service Changes**:
1. Edit file: `ocr-service/app/main.py`
2. Save
3. Restart: `docker compose restart ocr-service`
4. View logs: `docker compose logs -f ocr-service`

**AI Service Changes**:
1. Edit file: `ai-llm-service/app/main.py`
2. Save
3. Restart: `docker compose restart ai-llm-service`
4. View logs: `docker compose logs -f ai-llm-service`

### View Live Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f ocr-service
docker compose logs -f ai-llm-service
docker compose logs -f postgres
```

---

## 🐛 Troubleshooting

### Issue: Backend can't connect to database

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U dastern -d dastern -c "SELECT 1;"

# Check environment variables
docker compose exec backend env | grep DATABASE_URL
```

### Issue: OCR service returns error

```bash
# Check OCR logs
docker compose logs ocr-service | tail -50

# Test OCR directly
curl -X POST http://localhost:8000/health

# Restart OCR service
docker compose restart ocr-service
```

### Issue: AI enhancement not working

```bash
# Check AI service logs
docker compose logs ai-llm-service | tail -50

# Test AI directly
curl http://localhost:8001/health

# Restart AI service
docker compose restart ai-llm-service
```

### Issue: Frontend shows error

```bash
# Check backend logs
docker compose logs -f backend

# Check browser console (F12)
# Look for network errors or API failures
```

---

## 📈 Next Steps & Enhancements

### Immediate Improvements

1. **Better Medication Extraction**:
   - Current: Simple regex pattern matching
   - Enhancement: Use AI service to extract medications from OCR text
   - File to modify: `backend-nextjs/app/api/prescriptions/upload/route.ts`

2. **Image Storage**:
   - Current: Image URL stored as string only
   - Enhancement: Save images to storage (S3, local filesystem)
   - Add thumbnail generation

3. **User Authentication**:
   - Current: Using demo patient ID
   - Enhancement: Implement NextAuth.js
   - Add login/signup pages

4. **Reminder Notifications**:
   - Current: Reminders saved to database
   - Enhancement: Add push notifications, SMS, email
   - Implement reminder scheduler

### Advanced Features

1. **AI-Powered Medication Extraction**:
```typescript
// Send OCR text to AI for structured extraction
const aiResponse = await axios.post(`${aiServiceUrl}/extract-medications`, {
  text: ocrText,
  language: 'en'
});

// Save structured medications
for (const med of aiResponse.data.medications) {
  await query(`INSERT INTO medications ...`, [med]);
}
```

2. **Drug Interaction Checker**:
```typescript
// Check for interactions when adding new medication
const interactions = await checkDrugInteractions(patientId, newMedication);
```

3. **Prescription History Timeline**:
```typescript
// Get patient's prescription history
const history = await getPrescriptionHistory(patientId);
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL running and healthy
- [ ] Backend connected to database
- [ ] OCR service responding to `/process`
- [ ] AI service responding to `/correct-ocr`
- [ ] Web interface loading at `http://localhost:3000`
- [ ] Can upload prescription image
- [ ] OCR text extracted successfully
- [ ] Medications detected and saved to database
- [ ] Can query database for prescriptions
- [ ] Logs show no errors

---

## 📞 Quick Commands Reference

```bash
# Start everything
./docker-start.sh

# View all logs
docker compose logs -f

# Restart a service
docker compose restart backend

# Check service status
docker compose ps

# Connect to database
docker compose exec postgres psql -U dastern -d dastern

# Test health
curl http://localhost:3000/api/health

# Stop everything
docker compose stop

# Clean restart
docker compose down && docker compose up -d
```

---

**🎉 Your OCR system is now fully integrated with the database and ready to generate medication reminders!**
