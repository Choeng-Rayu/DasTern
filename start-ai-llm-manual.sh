#!/bin/bash
# Start AI LLM Service Manually (without Docker)

echo "Starting AI LLM Service on port 8001..."
cd /home/rayu/DasTern/ai-llm-service
source /home/rayu/DasTern/.venv/bin/activate

# Set environment variables
export OLLAMA_HOST="http://localhost:11434"
export LLM_MODEL="llama3.1:8b"
export PYTHONPATH=/home/rayu/DasTern/ai-llm-service:$PYTHONPATH

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
