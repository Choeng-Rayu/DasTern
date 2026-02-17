<<<<<<< HEAD
# Build stage for Python dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
=======
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
>>>>>>> 956213acb02fd8a10977582667da49fee5a0be8e


<<<<<<< HEAD
# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install Tesseract OCR and language packs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-khm \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/

# Create directories
RUN mkdir -p uploads results

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OCR_LANGUAGES=khm+eng+fra
ENV HOST=0.0.0.0
ENV PORT=8002

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
=======
EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
>>>>>>> 956213acb02fd8a10977582667da49fee5a0be8e
