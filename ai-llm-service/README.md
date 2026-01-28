# ai-llm-service

MT5-based FastAPI service for OCR correction and chat.

## Prerequisites
- Python 3.10+
- (Optional) GPU drivers/CUDA for faster inference

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Open:
- API docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

## Endpoints
- POST /api/v1/correct
- POST /api/v1/chat

## Notes
- The MT5 model is downloaded on first run (can take time and disk space).