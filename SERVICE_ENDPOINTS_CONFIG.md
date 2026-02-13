# Service Endpoints Configuration

## Port Allocation

| Service | Port | Host | Status |
|---------|------|------|--------|
| OCR Service (ocr-service-anti) | 8000 | 127.0.0.1 | ✅ Running |
| AI Service (main_ollama.py) | 8001 | 127.0.0.1 | ✅ Running |

## Endpoints

### OCR Service (Port 8000)

| Endpoint | Method | Path | Status |
|----------|--------|------|--------|
| Health Check | GET | `/health` | ✅ Added |
| Service Info | GET | `/` | ✅ Available |
| OCR Processing | POST | `/api/v1/ocr` | ✅ Available |
| Health (detailed) | GET | `/api/v1/health` | ✅ Available |

### AI Service (Port 8001)

| Endpoint | Method | Path | Status |
|----------|--------|------|--------|
| Health Check | GET | `/health` | ✅ Available |
| Service Info | GET | `/` | ✅ Available |
| OCR Correction | POST | `/correct-ocr` | ✅ Available |
| OCR API v1 | POST | `/api/v1/correct` | ✅ Available |
| Chat | POST | `/api/v1/chat` | ✅ Available |

## Flutter Configuration

### API Constants (`api_constants.dart`)
```
baseUrl: http://127.0.0.1 (on iOS/macOS)
ocrBaseUrl: http://127.0.0.1:8000/api/v1
aiBaseUrl: http://127.0.0.1:8001/api/v1
```

### Providers
- **OCRProvider**: Connects to `http://127.0.0.1:8000` → calls `/health`
- **AIProvider**: Connects to `http://127.0.0.1:8001` → calls `/health`

## Startup Commands

### OCR Service
```bash
cd /Users/macbook/CADT/DasTern/ocr-service-anti
python main.py 8000
# OR
python main.py  # Defaults to port 8000
```

### AI Service
```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service
python app/main_ollama.py
# OR
uvicorn app.main_ollama:app --host 127.0.0.1 --port 8001
```

## Service Dependencies

- **OCR Service**: Requires Tesseract OCR
- **AI Service**: Requires Ollama running on `http://localhost:11434`

## Verification Commands

### Check OCR Health
```bash
curl -i http://127.0.0.1:8000/health
# Should return: { "status": "healthy", "service": "ocr-service", ... }
```

### Check AI Health
```bash
curl -i http://127.0.0.1:8001/health
# Should return: { "status": "healthy", "service": "ollama-ai-service", ... }
```

## Flutter Connection Flow

1. Flutter starts → Initializes OCRProvider + AIProvider
2. OCRProvider.checkServiceHealth() → GET `http://127.0.0.1:8000/health`
3. AIProvider.checkServiceHealth() → GET `http://127.0.0.1:8001/health`
4. Both return 200 → Services marked as healthy ✅
5. User selects image → OCRProvider sends to `/api/v1/ocr`
6. OCR returns text → AIProvider sends to `/api/v1/correct` for correction
