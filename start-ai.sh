#!/bin/bash
cd /home/rayu/DasTern
source .venv/bin/activate
cd ai-llm-service
uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
