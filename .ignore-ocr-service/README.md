# ocr-service

FastAPI OCR backend for prescription scanning (English, Khmer, French).

## Prerequisites
- Python 3.10+
- Tesseract OCR + language data (eng, khm, fra)

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install Tesseract (Ubuntu/Debian example):
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-khm tesseract-ocr-fra
```

You can also run the helper script:
```bash
./setup.sh
```

## Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Endpoints
- POST /ocr (multipart file)
- POST /ocr/base64
- GET /languages