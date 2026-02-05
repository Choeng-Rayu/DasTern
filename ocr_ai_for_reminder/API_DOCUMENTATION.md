# Flutter App - Backend API Documentation

## Overview

The Flutter app communicates with two backend services:
1. **OCR Service** (ocr-service-anti): Handles prescription image scanning
2. **AI Service** (ai-llm-service): Handles text correction and medication extraction

## Base URL Configuration

Default: `http://localhost:8000`

Update in `lib/utils/constants.dart`:
```dart
static const String apiBaseUrl = 'http://localhost:8000';
```

## API Endpoints

### OCR Service Endpoints

#### 1. Process Prescription Image
**Endpoint:** `POST /api/v1/ocr`

**Headers:**
```
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): Binary image file (JPG, PNG)
- `languages` (optional): Comma-separated language codes (default: "eng+khm+fra")
- `skip_enhancement` (optional): Boolean (default: false)

**Request Example:**
```bash
curl -X POST http://localhost:8000/api/v1/ocr \
  -F "file=@prescription.jpg" \
  -F "languages=eng+khm+fra" \
  -F "skip_enhancement=false"
```

**Response (200 OK):**
```json
{
  "meta": {
    "languages": ["eng", "khm", "fra"],
    "dpi": 300,
    "processing_time_ms": 2500.0,
    "model_version": "default",
    "stage_times": {
      "enhancement": 500.0,
      "layout": 800.0,
      "recognition": 1200.0
    },
    "image_size": {
      "width": 2400,
      "height": 3200
    }
  },
  "quality": {
    "blur": "low",
    "blur_score": 150.5,
    "contrast": "high",
    "contrast_score": 45.3,
    "skew_angle": 0.5,
    "dpi": 300,
    "is_grayscale": false
  },
  "blocks": [
    {
      "type": "header",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 2400,
        "height": 200
      },
      "lines": [
        {
          "text": "PRESCRIPTION",
          "bbox": {
            "x": 100,
            "y": 50,
            "width": 800,
            "height": 80
          },
          "confidence": 0.95,
          "language": "eng",
          "tags": []
        }
      ],
      "raw_text": "PRESCRIPTION"
    }
  ],
  "full_text": "PRESCRIPTION\nPatient: John Doe\nDate: 2026-02-02\nDrugs:\n1. Aspirin 500mg...",
  "success": true,
  "error": null
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "error": "Invalid image format",
  "full_text": ""
}
```

---

#### 2. Quality Analysis Only
**Endpoint:** `POST /api/v1/ocr/analyze`

**Parameters:**
- `file` (required): Binary image file
- `skip_full_ocr` (optional): Skip full OCR, only analyze quality

**Response:**
```json
{
  "quality": {
    "blur": "low",
    "blur_score": 150.5,
    "contrast": "high",
    "contrast_score": 45.3,
    "skew_angle": 0.5,
    "dpi": 300,
    "is_grayscale": false
  },
  "meta": {
    "processing_time_ms": 500.0
  }
}
```

---

#### 3. Health Check
**Endpoint:** `GET /`

**Response (200 OK):**
```json
{
  "service": "OCR Service",
  "version": "1.0.0",
  "description": "Layer-by-layer OCR for Cambodian prescriptions",
  "docs": "/docs"
}
```

---

### AI Service Endpoints

#### 1. Correct OCR Text
**Endpoint:** `POST /api/v1/correct`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "raw_text": "Prescrption for patient John...",
  "language": "en",
  "context": {
    "format": "prescription",
    "domain": "healthcare"
  }
}
```

**Parameters:**
- `raw_text` (required): Raw OCR text to correct
- `language` (optional): Language code ("en", "km", "fr") - default: "en"
- `context` (optional): Additional context for correction

**Response (200 OK):**
```json
{
  "corrected_text": "Prescription for patient John...",
  "confidence": 0.92,
  "changes_made": [
    {
      "original": "Prescrption",
      "corrected": "Prescription"
    }
  ],
  "language": "en",
  "metadata": {
    "model_used": "MT5-small",
    "processing_time": 1200
  }
}
```

---

#### 2. Extract Medication Reminders
**Endpoint:** `POST /api/v1/extract-reminders`

**Request Body:**
```json
{
  "raw_ocr_json": {
    "full_text": "Aspirin 500mg twice daily for 7 days...",
    "meta": {...},
    "quality": {...},
    "blocks": [...]
  }
}
```

**Response (200 OK):**
```json
{
  "medications": [
    {
      "name": "Aspirin",
      "dosage": "500mg",
      "times": ["morning", "evening"],
      "times_24h": ["08:00", "20:00"],
      "repeat": "daily",
      "duration_days": 7,
      "notes": "Take with food"
    }
  ],
  "success": true,
  "metadata": {
    "extracted_count": 1,
    "confidence": 0.89
  }
}
```

---

#### 3. Health Check
**Endpoint:** `GET /`

**Response:**
```json
{
  "service": "AI LLM Service",
  "status": "running",
  "model": "MT5-small",
  "capabilities": ["ocr_correction", "chatbot"]
}
```

---

## Data Models

### Quality Metrics

```dart
class QualityMetrics {
  String blur;           // "low", "medium", "high"
  double blurScore;      // Raw blur score
  String contrast;       // "low", "ok", "high"
  double contrastScore;  // Raw contrast score
  double skewAngle;      // Degrees
  int? dpi;              // Image DPI
  bool isGrayscale;      // Grayscale flag
}
```

### Block Types

```
- "header": Title/header section
- "table": Tabular data
- "text": Regular text
- "footer": Footer section
- "signature": Signature area
- "qr_code": QR code
- "vital_signs": Vital signs section
```

### Medication Info

```dart
class MedicationInfo {
  String name;                    // "Aspirin"
  String dosage;                  // "500mg"
  List<String> times;             // ["morning", "noon", "evening"]
  List<String> times24h;          // ["08:00", "12:00", "18:00"]
  String repeat;                  // "daily", "weekly"
  int? durationDays;              // 7
  String notes;                   // "Take with food"
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check request format |
| 408 | Timeout | Retry with backoff |
| 422 | Validation Error | Check input data |
| 500 | Server Error | Retry or contact support |
| 503 | Service Unavailable | Retry later |

### Error Response Format

```json
{
  "detail": "Error description",
  "error": "error_code",
  "status": 400
}
```

---

## Integration Examples

### 1. Complete OCR Processing Flow

```dart
// 1. Upload image
final response = await apiClient.uploadImageForOCR(imagePath);

// 2. Parse OCR response
final ocrData = OCRResponse.fromJson(jsonData);

// 3. Extract text
final text = ocrData.fullText;

// 4. Correct text with AI
final corrected = await aiService.correctOCRText(text);

// 5. Extract medications
final medications = await aiService.extractReminders(ocrData.toJson());
```

### 2. Error Handling

```dart
try {
  final result = await ocrService.processImage(imagePath);
  
  if (!result.success) {
    throw Exception(result.error);
  }
  
  // Process result
} on TimeoutException {
  // Handle timeout
  print('Request timed out, please try again');
} on SocketException {
  // Handle network error
  print('Network error, check connection');
} catch (e) {
  // Handle other errors
  print('Error: $e');
}
```

### 3. Retry with Backoff

```dart
Future<T> retryWithBackoff<T>(
  Future<T> Function() operation, {
  int maxAttempts = 3,
}) async {
  for (int i = 0; i < maxAttempts; i++) {
    try {
      return await operation();
    } catch (e) {
      if (i == maxAttempts - 1) rethrow;
      
      // Exponential backoff: 1s, 2s, 4s
      final delay = Duration(seconds: pow(2, i).toInt());
      await Future.delayed(delay);
    }
  }
  
  throw Exception('Max retry attempts reached');
}
```

---

## Rate Limiting

- OCR processing: 10 requests/minute per IP
- AI correction: 30 requests/minute per IP
- Health checks: Unlimited

---

## Performance Optimization

### 1. Image Compression
```dart
// Compress before upload
image.compress(85); // 85% quality
```

### 2. Caching
```dart
// Cache OCR results
final cached = await cache.get('ocr_${imagePath}');
```

### 3. Batch Processing
```dart
// Process multiple images
final futures = images.map((img) => ocrService.processImage(img));
final results = await Future.wait(futures);
```

---

## Testing API Endpoints

### Using cURL

```bash
# OCR endpoint
curl -X POST http://localhost:8000/api/v1/ocr \
  -F "file=@prescription.jpg" \
  -H "Accept: application/json"

# AI endpoint
curl -X POST http://localhost:8001/api/v1/correct \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Sample text",
    "language": "en"
  }'

# Health check
curl http://localhost:8000/
```

### Using Postman

1. Create new request
2. Set method to POST
3. Set URL to `http://localhost:8000/api/v1/ocr`
4. Go to Body → form-data
5. Add key "file" (File type)
6. Select image file
7. Send request

---

## Documentation

- OCR Service Docs: `http://localhost:8000/docs`
- AI Service Docs: `http://localhost:8001/docs`
