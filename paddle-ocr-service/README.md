# OCR Service

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
pip install -r requirements.txt
```

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
