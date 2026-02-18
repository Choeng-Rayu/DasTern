# Flutter Connection Verification Checklist

## ✅ Fixed Issues
- [x] OCRProvider now uses `127.0.0.1:8000` instead of `localhost:8000`
- [x] AIProvider now uses `127.0.0.1:8001` instead of `localhost:8001`
- [x] Both import ApiConstants to get correct base URLs
- [x] Both services have `/health` endpoints

## 🚀 Quick Start

### Step 1: Start Ollama (if not already running)
```bash
ollama serve
# Should show: Listening on 127.0.0.1:11434
```

### Step 2: Start Both Services
```bash
/Users/macbook/CADT/DasTern/start_all_services.sh
```

Or run manually:

**Terminal 1 - OCR Service (Port 8000)**
```bash
cd /Users/macbook/CADT/DasTern/ocr-service-anti
python main.py 8000
```

**Terminal 2 - AI Service (Port 8001)**
```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service
python app/main_ollama.py
```

### Step 3: Verify Services Are Healthy

```bash
# Should return 200 with status: "healthy"
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8001/health
```

### Step 4: Launch Flutter App
```bash
cd /Users/macbook/CADT/DasTern/ocr_ai_for_reminder
flutter run -d macos  # or your device/emulator
```

## ✅ Expected Behavior

When Flutter app starts:
- ✅ No more "Operation not permitted" errors
- ✅ Logger shows: "OCR Service is healthy" 
- ✅ Health checks pass for both services
- ✅ App initializes without errors

## 🔍 Troubleshooting

### If you still get connection errors:

1. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   # Should return list of models
   ```

2. **Check services are actually listening:**
   ```bash
   lsof -i :8000  # Should show Python process
   lsof -i :8001  # Should show Python process
   ```

3. **Verify network binding on macOS:**
   ```bash
   # Both services should bind to 127.0.0.1, not 0.0.0.0
   ss -tuln | grep "800"
   # Should show 127.0.0.1:8000 and 127.0.0.1:8001
   ```

4. **Check Flutter uses correct addresses:**
   - Open: `ocr_ai_for_reminder/lib/core/constants/api_constants.dart`
   - Verify: `baseUrl` returns `'http://127.0.0.1'` for iOS/macOS
   - Verify: `defaultOcrPort = '8000'`
   - Verify: `defaultAiPort = '8001'`

## 📋 Service Configuration Summary

| Service | Port | Host | Health Endpoint | Status |
|---------|------|------|----------------|--------|
| OCR | 8000 | 127.0.0.1 | GET `/health` | ✅ Fixed |
| AI | 8001 | 127.0.0.1 | GET `/health` | ✅ Fixed |
| Ollama | 11434 | localhost | N/A | ✅ Required |

## 🛑 Kill Services

```bash
# Kill all Python services
pkill -f "python.*main"
pkill -f "uvicorn"

# Or manually if needed
kill $(lsof -t -i :8000)
kill $(lsof -t -i :8001)
```
