# ===========================================
# DasTern OCR Service
# Python 3.10 + PaddleOCR + LayoutLMv3
# ===========================================

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OCR and image processing
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with retry and timeout handling
COPY requirements.txt .
RUN pip install \
    --default-timeout=1000 \
    --retries 5 \
    -r requirements.txt

# Copy source
COPY . .

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
