#!/bin/bash
source /home/rayu/DasTern/.venv/bin/activate
export AI_SERVICE_HOST=0.0.0.0
export AI_SERVICE_PORT=8001
export OLLAMA_MODEL=llama3.2:3b

echo "Restarting AI Service..."
cd /home/rayu/DasTern/ai-llm-service
# Kill existing on port 8001
fuser -k 8001/tcp
python -m app.main > ai_service_run.log 2>&1 &
echo "AI Service restarted. Check ai_service_run.log for status."
