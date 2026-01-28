# ===========================================
# DasTern OCR Service
# Python 3.10 + Tesseract OCR (Multi-Language)
# Supports: Khmer, English, French
# ===========================================

FROM python:3.10-slim

WORKDIR /app

# Set PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Install system dependencies for OCR and image processing
# - Tesseract OCR with language packs (Khmer, English, French)
# - OpenCV requires: libGL, libglib, libsm, libxext, libxrender, libgomp
RUN apt-get update && apt-get install -y \
    # Tesseract OCR and language packs
    tesseract-ocr \
    tesseract-ocr-khm \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    # OpenCV dependencies
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && echo "Installed Tesseract languages:" \
    && tesseract --list-langs

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
