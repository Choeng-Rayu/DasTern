# Docker Configuration Updates

## ✅ Changes Made to Docker Setup

### 1. **OCR Service Dockerfile** (NEW)
- **File**: [ocr-service/Dockerfile](ocr-service/Dockerfile)
- **Changes**:
  - Created Dockerfile for OCR service
  - Base: Python 3.10-slim
  - Installed system dependencies (libsm6, libxext6 for OpenCV/image processing)
  - Port: **8002** (was 8000)
  - Added curl for health checks

### 2. **AI LLM Service Dockerfile** (UPDATED)
- **File**: [ai-llm-service/Dockerfile](ai-llm-service/Dockerfile)
- **Changes**:
  - Updated from MT5 to LLaMA-based service
  - Added build-essential for compilation
  - Added `/app/models` volume mount for LLaMA weights
  - Removed `--reload` flag (for production)
  - Port: **8001** (unchanged)

### 3. **Docker-Compose** (UPDATED)
- **File**: [docker-compose.yml](docker-compose.yml)
- **Changes**:

#### OCR Service:
```yaml
ocr-service:
  - Port changed: 8000 → 8002
  - Added environment variables:
    - PYTHONUNBUFFERED=1
    - OCR_LANG=en,kh
  - Added health checks
  - Added restart policy
```

#### AI LLM Service:
```yaml
ai-llm-service:
  - Port: 8001 (unchanged)
  - Added environment variables:
    - PYTHONUNBUFFERED=1
    - MODEL_PATH=/app/models/llama/weights.gguf
    - ALLOWED_LANGUAGES=en,kh,fr
  - Added models volume mount
  - Added health checks
  - Added restart policy
```

#### Backend Service:
```yaml
backend:
  - Updated depends_on to use service_healthy conditions
  - Added environment variables:
    - OCR_SERVICE_URL=http://ocr-service:8002
    - LLM_SERVICE_URL=http://ai-llm-service:8001
    - DATABASE_URL (auto-configured from .env)
  - Added health checks
```

### 4. **.env.example** (UPDATED)
- **File**: [.env.example](.env.example)
- **Changes**:
  - Added database environment variables (DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
  - Updated OCR_SERVICE_URL: 8000 → 8002
  - Renamed AI_SERVICE_URL → LLM_SERVICE_URL
  - Added OCR configuration (OCR_LANG, OCR_CONFIDENCE_THRESHOLD)
  - Added LLM configuration (MODEL_PATH, LANGUAGES, MAX_TOKENS, TEMPERATURE)
  - Added PYTHON_ENV variable

## 📋 Service Ports Summary

| Service | Port | URL (Internal) | URL (Host) |
|---------|------|--------|------|
| Backend | 3000 | N/A | http://localhost:3000 |
| PostgreSQL | 5432 | postgres:5432 | localhost:5432 |
| OCR Service | 8002 | ocr-service:8002 | http://localhost:8002 |
| LLM Service | 8001 | ai-llm-service:8001 | http://localhost:8001 |

## 🚀 Next Steps

1. **Copy .env.example to .env**:
   ```bash
   cp .env.example .env
   ```

2. **Update .env with your values** (especially JWT_SECRET, NEXTAUTH_SECRET)

3. **Build and start containers**:
   ```bash
   docker compose build
   docker compose up -d
   ```

4. **Download LLaMA model** (for ai-llm-service):
   - Place quantized GGUF model in `ai-llm-service/models/llama/weights.gguf`

5. **Verify health checks**:
   ```bash
   docker ps  # All services should show healthy
   ```

## ⚠️ Important Notes

- **Health checks are now properly configured** - backend waits for both services to be healthy
- **OCR service now on port 8002** - update any references from 8000
- **LLM service expects model at `/app/models/llama/weights.gguf`** - mount or download separately
- **All services on same Docker network** - can communicate internally using service names
- **Environment variables auto-passed** - backend automatically gets service URLs
