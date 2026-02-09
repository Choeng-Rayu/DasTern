#!/bin/bash
# Enable immediate exit on error
set -e

# Activate virtual environment
source /home/rayu/DasTern/.venv/bin/activate

# Set environment variables
export AI_SERVICE_HOST=0.0.0.0
export AI_SERVICE_PORT=8001
export OLLAMA_MODEL=llama3.2:3b
export LOG_LEVEL=INFO
export TRANSFORMERS_VERBOSITY=info

echo "🚀 Checking dependencies..."
# Ensure transformers is installed (fail fast if not)
pip install transformers torch sentencepiece --quiet

echo "🚀 Starting AI LLM Service (Foreground)..."
echo "logs will appear below:"
echo "-----------------------------------"

# Run as module to ensure imports work
cd /home/rayu/DasTern/ai-llm-service
python -m app.main
