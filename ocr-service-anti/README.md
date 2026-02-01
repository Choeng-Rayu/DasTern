# OCR Service

A layer-by-layer OCR service for scanning complex Cambodian prescriptions containing mixed Khmer/English/French text, tables, stamps, and symbols.

## Features

- **7-Layer Architecture**: Modular, scalable design
- **Multi-language Support**: English, Khmer, French
- **Layout Analysis**: Table detection, column separation
- **Fine-tuning Support**: Train custom models for specific fonts
- **AI-Ready Output**: JSON with bounding boxes

## Quick Start

### Prerequisites

```bash
# Fedora/RHEL
sudo dnf install tesseract tesseract-langpack-eng tesseract-langpack-khm tesseract-langpack-fra zbar

# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-khm tesseract-ocr-fra libzbar0
```

### Installation

```bash
cd ocr-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the Service

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ocr` | POST | Process prescription image |
| `/api/v1/ocr/analyze` | POST | Quality analysis only |
| `/api/v1/health` | GET | Health check |
| `/api/v1/info` | GET | Service info |

### Example Usage

```bash
curl -X POST "http://localhost:8000/api/v1/ocr" \
  -F "file=@prescription.jpg"
```

## Architecture

```
Image Input → Validation → Quality Analysis → Preprocessing → Layout Analysis → OCR → Post-processing → JSON Output
```

## Project Structure

```
ocr-service/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Config, exceptions, pipeline
│   ├── intake/        # Layer 1: Validation
│   ├── quality/       # Layer 2: Quality analysis
│   ├── preprocess/    # Layer 3: Image enhancement
│   ├── layout/        # Layer 4: Layout detection
│   ├── ocr/           # Layer 5: Tesseract OCR
│   ├── postprocess/   # Layer 6: Text cleaning
│   ├── builder/       # Layer 7: JSON builder
│   ├── training/      # Fine-tuning module
│   └── schemas/       # Pydantic models
├── training_data/     # Training resources
├── tests/             # Unit tests
└── requirements.txt
```

## License

MIT
