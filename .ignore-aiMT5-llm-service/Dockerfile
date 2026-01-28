# ===========================================
# DasTern AI LLM Service
# Python 3.10 + LLaMA
# ===========================================

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with retry and timeout handling
COPY requirements.txt .
RUN pip install \
    --default-timeout=1000 \
    --retries 5 \
    -r requirements.txt

# Copy source
COPY . .

# Model files should be mounted or downloaded separately
VOLUME ["/app/models"]

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
