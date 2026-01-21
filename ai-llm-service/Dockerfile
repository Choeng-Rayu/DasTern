# ===========================================
# DasTern AI LLM Service
# Python 3.10 + MT5
# ===========================================

FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies with retry and timeout handling
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 5 \
    -r requirements.txt

# Copy source
COPY . .

# Model files stay mounted or baked later (good for MVP)

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
