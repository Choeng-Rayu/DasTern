# ===========================================
# DasTern OCR Service
# Python 3.10 + PaddleOCR + LayoutLMv3
# ===========================================

FROM python:3.10-slim

WORKDIR /app

# Set PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Install system dependencies for OCR and image processing
# OpenCV requires: libGL, libglib, libsm, libxext, libxrender, libgomp
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    curl \
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
