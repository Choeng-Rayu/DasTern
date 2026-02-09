# Port Configuration Guide

All service ports are now configurable via environment variables (.env files). This allows you to easily change ports when the default ones are busy.

## Services and Default Ports

| Service | Default Port | Environment Variable |
|---------|--------------|---------------------|
| OCR Service | 8000 | `OCR_SERVICE_PORT` |
| AI-LLM Service | 8001 | `AI_SERVICE_PORT` |
| Ollama | 11434 | `OLLAMA_BASE_URL` |

## Configuration Files

### 1. AI-LLM Service (`ai-llm-service/.env`)

```env
# Server Configuration
AI_SERVICE_HOST=0.0.0.0
AI_SERVICE_PORT=8001

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300

# Model Configuration
DEFAULT_MODEL=llama3.1:8b
REMINDER_MODEL=llama3.2:3b
```

### 2. OCR Service (`ocr-service-anti/.env`)

```env
# Server Configuration
OCR_SERVICE_HOST=0.0.0.0
OCR_SERVICE_PORT=8000

# Service URLs
AI_LLM_SERVICE_URL=http://localhost:8001
```

### 3. Flutter App (`ocr_ai_for_reminder/.env`)

```env
# API Service URLs
API_BASE_URL=http://localhost
OCR_SERVICE_PORT=8000
AI_SERVICE_PORT=8001

# For local development
OCR_SERVICE_URL=http://localhost:8000
AI_LLM_SERVICE_URL=http://localhost:8001
```

## How to Change Ports

### Scenario: Port 8001 is already in use

If you get the error: `address already in use` for port 8001:

1. **Edit `ai-llm-service/.env`**:
   ```env
   AI_SERVICE_PORT=8002  # Change to any available port
   ```

2. **Update `ocr-service-anti/.env`** to match:
   ```env
   AI_LLM_SERVICE_URL=http://localhost:8002
   ```

3. **Update `ocr_ai_for_reminder/.env`**:
   ```env
   AI_SERVICE_PORT=8002
   AI_LLM_SERVICE_URL=http://localhost:8002
   ```

4. **Restart the services** for changes to take effect.

### Scenario: Port 8000 is already in use

1. **Edit `ocr-service-anti/.env`**:
   ```env
   OCR_SERVICE_PORT=8003  # Change to any available port
   ```

2. **Update `ocr_ai_for_reminder/.env`**:
   ```env
   OCR_SERVICE_PORT=8003
   OCR_SERVICE_URL=http://localhost:8003
   ```

3. **Restart the services**.

## Running Services with Custom Ports

### Method 1: Using .env files (Recommended)
Just edit the `.env` file and run the service normally:

```bash
# AI-LLM Service
cd ai-llm-service
python app/main_ollama.py

# OCR Service
cd ocr-service-anti
python main.py
```

### Method 2: CLI Override for OCR Service
The OCR service still supports CLI port override:

```bash
cd ocr-service-anti
python main.py 8005  # Use port 8005 instead
```

### Method 3: Export environment variables
You can also set environment variables directly:

```bash
# AI-LLM Service
export AI_SERVICE_PORT=8002
cd ai-llm-service
python app/main_ollama.py

# OCR Service
export OCR_SERVICE_PORT=8003
cd ocr-service-anti
python main.py
```

## Flutter App Port Configuration

For the Flutter app, you can configure ports at compile time:

```bash
# Build with custom ports
flutter run --dart-define=OCR_SERVICE_PORT=8003 --dart-define=AI_SERVICE_PORT=8002
```

Or edit the `.env` file and the app will use those values by default.

## Checking Which Ports Are in Use

### Linux/Mac
```bash
# Check if a specific port is in use
lsof -i :8001

# Check all listening ports
netstat -tuln | grep LISTEN

# Find what's using a specific port
sudo ss -lptn 'sport = :8001'
```

### Kill Process on Port
```bash
# Find the PID
lsof -ti :8001

# Kill the process
kill -9 $(lsof -ti :8001)
```

## Testing Service Connectivity

After changing ports, test the services:

```bash
# Test OCR Service
curl http://localhost:8000/

# Test AI-LLM Service
curl http://localhost:8001/

# Test Ollama
curl http://localhost:11434/api/tags
```

## Docker Compose Port Mapping

If using Docker, update `docker-compose.yml` port mappings to match:

```yaml
services:
  ocr-service:
    ports:
      - "8000:8000"  # Change left side to match your .env port
  
  ai-llm-service:
    ports:
      - "8001:8001"  # Change left side to match your .env port
```

## Troubleshooting

### "Address already in use" error
1. Check what's using the port: `lsof -i :8001`
2. Either kill that process or change your service port
3. Make sure to update all interconnected services

### Services can't connect to each other
1. Verify all services use consistent port configurations
2. Check `.env` files in all three services match
3. Restart all services after changing ports

### Flutter app can't connect
1. For Android emulator, use `10.0.2.2` instead of `localhost`
2. For iOS simulator, use `127.0.0.1`
3. Ensure ports in Flutter match the actual running services
4. Rebuild the app after changing ports

## Quick Port Change Script

Save this as `change_ports.sh`:

```bash
#!/bin/bash

NEW_OCR_PORT=${1:-8000}
NEW_AI_PORT=${2:-8001}

echo "Changing OCR port to: $NEW_OCR_PORT"
echo "Changing AI port to: $NEW_AI_PORT"

# Update ai-llm-service
sed -i "s/^AI_SERVICE_PORT=.*/AI_SERVICE_PORT=$NEW_AI_PORT/" ai-llm-service/.env

# Update ocr-service-anti
sed -i "s/^OCR_SERVICE_PORT=.*/OCR_SERVICE_PORT=$NEW_OCR_PORT/" ocr-service-anti/.env
sed -i "s|^AI_LLM_SERVICE_URL=.*|AI_LLM_SERVICE_URL=http://localhost:$NEW_AI_PORT|" ocr-service-anti/.env

# Update Flutter app
sed -i "s/^OCR_SERVICE_PORT=.*/OCR_SERVICE_PORT=$NEW_OCR_PORT/" ocr_ai_for_reminder/.env
sed -i "s/^AI_SERVICE_PORT=.*/AI_SERVICE_PORT=$NEW_AI_PORT/" ocr_ai_for_reminder/.env
sed -i "s|^OCR_SERVICE_URL=.*|OCR_SERVICE_URL=http://localhost:$NEW_OCR_PORT|" ocr_ai_for_reminder/.env
sed -i "s|^AI_LLM_SERVICE_URL=.*|AI_LLM_SERVICE_URL=http://localhost:$NEW_AI_PORT|" ocr_ai_for_reminder/.env

echo "✅ Port configuration updated!"
echo "Please restart all services."
```

Usage:
```bash
chmod +x change_ports.sh
./change_ports.sh 8003 8002  # OCR=8003, AI=8002
```

## Summary

All ports are now centralized in `.env` files for easy management. When a port is busy:
1. Edit the `.env` file(s)
2. Update any dependent services
3. Restart services
4. Test connectivity

This flexible configuration makes it easy to avoid port conflicts and run multiple instances if needed.
