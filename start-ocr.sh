#!/bin/bash
cd /home/rayu/DasTern
source .venv/bin/activate
cd ocr-service
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
