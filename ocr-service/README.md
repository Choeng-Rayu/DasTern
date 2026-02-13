# OCR Service

<<<<<<< HEAD
Tesseract-based multilingual OCR service for extracting raw text from prescription images.

## Features

- **Multilingual OCR**: Khmer (khm), English (eng), French (fra)
- **Bounding Boxes**: Position and size of each detected text element
- **Confidence Scores**: Accuracy confidence for each element
- **Structure Metadata**: Block, paragraph, line, and word information
- **Image Preprocessing**: Denoising and adaptive thresholding

## Important Design Principle

This service provides **RAW OCR output only**:
- ✅ Extract text
- ✅ Keep bounding boxes
- ✅ Keep language mix
- ✅ Keep structure metadata

This service does **NOT**:
- ❌ Understand tables
- ❌ Understand medicine
- ❌ Translate languages
- ❌ Convert time
- ❌ Detect dosage
- ❌ Fix OCR errors

Use the AI/LLM service for text interpretation and correction.

## Prerequisites

### System Dependencies

```bash
# Install Tesseract OCR
sudo apt update
sudo apt install -y tesseract-ocr

# Install language packs (REQUIRED)
sudo apt install -y \
  tesseract-ocr-eng \
  tesseract-ocr-fra \
  tesseract-ocr-khm

# Verify installation
tesseract --list-langs
# Should show: eng, fra, khm
```

## Installation

### Using Virtual Environment

```bash
cd ocr-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
=======
Document AI service for prescription processing using PaddleOCR and LayoutLMv3.

## Architecture

```
ocr-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── schemas.py           # Data contracts (OCRBlock, OCRResult)
│   ├── pipeline.py          # Pipeline orchestration
│   ├── confidence.py        # Confidence scoring
│   │
│   ├── ocr/
│   │   ├── __init__.py
│   │   └── paddle_engine.py # PaddleOCR text extraction
│   │
│   ├── layout/
│   │   ├── __init__.py
│   │   ├── layoutlmv3.py    # Document structure understanding
│   │   ├── grouping.py      # Block grouping logic
│   │   └── key_value.py     # Key-value extraction
│   │
│   └── rules/
│       ├── __init__.py
│       ├── medical_terms.py # Medical term corrections
│       └── khmer_fix.py     # Khmer-specific fixes
│
├── requirements.txt
└── README.md
```

## Setup

1. Create virtual environment:
```bash
cd ocr-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
>>>>>>> 956213acb02fd8a10977582667da49fee5a0be8e
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

<<<<<<< HEAD
### Using Docker

```bash
# Build image
docker build -t ocr-service .

# Run container
docker run -p 8002:8002 ocr-service
```

## Running the Service

### Development Mode

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Production Mode

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

## API Endpoints

### Health Check
```
GET /health
GET /api/v1/ocr/health
```

### Extract Text
```
POST /api/v1/ocr/extract
Content-Type: multipart/form-data

Parameters:
- file: Image file (required)
- apply_preprocessing: boolean (default: true)
- languages: string (default: "khm+eng+fra")
- include_low_confidence: boolean (default: true)
- include_stats: boolean (default: true)
```

### Extract and Save
```
POST /api/v1/ocr/extract-and-save
Content-Type: multipart/form-data

Parameters:
- file: Image file (required)
- output_name: string (optional, default: tesseract_result_{N})
- apply_preprocessing: boolean (default: true)
- languages: string (optional)
```

### Get Available Languages
```
GET /api/v1/ocr/languages
```

## Example Response

```json
{
  "success": true,
  "page": 1,
  "raw": [
    {
      "text": "លេប",
      "confidence": 92,
      "bbox": { "x": 120, "y": 450, "w": 50, "h": 20 },
      "block": 1,
      "paragraph": 1,
      "line": 1,
      "word": 1
    },
    {
      "text": "2x/day",
      "confidence": 85,
      "bbox": { "x": 320, "y": 450, "w": 80, "h": 22 },
      "block": 1,
      "paragraph": 1,
      "line": 1,
      "word": 2
    }
  ],
  "stats": {
    "total_words": 2,
    "avg_confidence": 88.5,
    "min_confidence": 85,
    "max_confidence": 92,
    "total_blocks": 1,
    "total_lines": 1
  },
  "languages_used": "khm+eng+fra"
}
```

## Configuration

See `.env.example` for all configuration options.

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| OCR_LANGUAGES | OCR language string | khm+eng+fra |
| OCR_OEM | OCR Engine Mode | 3 |
| OCR_PSM | Page Segmentation Mode | 6 |
| PORT | Service port | 8002 |

## Testing

```bash
# Using curl
curl -X POST "http://localhost:8002/api/v1/ocr/extract" \
  -F "file=@test_image.jpg"

# Using Python
import requests

with open("test_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8002/api/v1/ocr/extract",
        files={"file": f}
    )
print(response.json())
```

## Architecture

```
ocr-service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   └── ocr.py           # OCR endpoints
│   ├── core/
│   │   ├── config.py        # Settings
│   │   └── logger.py        # Logging
│   ├── ocr/
│   │   ├── preprocess/
│   │   │   └── opencv.py    # Image preprocessing
│   │   ├── engines/
│   │   │   └── tesseract.py # Tesseract wrapper
│   │   ├── extractors/
│   │   │   └── raw_text.py  # Text extraction
│   │   └── parsers/
│   │       └── tesseract_parser.py  # Output parsing
│   ├── models/
│   │   ├── bbox.py          # Bounding box model
│   │   └── raw_ocr.py       # OCR response models
│   └── utils/
│       └── image.py         # Image utilities
├── Dockerfile
├── requirements.txt
└── README.md
```

## Future Improvements

1. **Custom Khmer Words**: Add user words file for improved Khmer recognition
   ```bash
   # Create tessdata/khm.user-words with common Khmer medical terms
   ```

2. **PDF Support**: Add PDF to image conversion

3. **Multi-page Documents**: Support batch processing

4. **GPU Acceleration**: Use CUDA for faster processing
=======
3. Run service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## API Endpoints

### POST /ocr
Process prescription image with OCR

**Request:**
- Multipart form data with image file

**Response:**
```json
{
  "blocks": [
    {
      "text": "Paracetamol 500mg",
      "box": {"x1": 10, "y1": 20, "x2": 200, "y2": 40},
      "confidence": 0.95,
      "block_type": "body"
    }
  ]
}
```

## Implementation Status

🚧 **Structure Ready - Implementation Pending**

All files are created with TODO markers for implementation.

## Next Steps

1. Implement PaddleOCR integration in `paddle_engine.py`
2. Add LayoutLMv3 model loading in `layoutlmv3.py`
3. Implement grouping algorithms in `grouping.py`
4. Build medical term dictionary in `medical_terms.py`
5. Connect pipeline in `pipeline.py`
6. Test with sample prescription images
>>>>>>> 956213acb02fd8a10977582667da49fee5a0be8e
