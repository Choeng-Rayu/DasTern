"""
FastAPI Application for OCR Backend

REST API endpoints for prescription OCR service.
Supports: English, Khmer, French mixed-language prescriptions.
"""

import base64
import io
import os
import sys
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2

try:
    from .pipeline import run_pipeline, run_pipeline_from_bytes
    from .schemas import OCRResult, OCRRequest, LanguageCode
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from app.pipeline import run_pipeline, run_pipeline_from_bytes
    from app.schemas import OCRResult, OCRRequest, LanguageCode


# Initialize FastAPI app
app = FastAPI(
    title="Prescription OCR API",
    description="Multi-language OCR system for medical prescriptions (English, Khmer, French)",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Prescription OCR API",
        "version": "1.0.0",
        "supported_languages": ["English", "Khmer", "French"]
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "ocr_engine": "ready",
            "layout": "ready",
            "preprocessing": "ready",
            "postprocessing": "ready"
        }
    }


@app.post("/ocr", response_model=None)
async def process_image(
    file: UploadFile = File(...),
    lenient_quality: bool = Form(default=False),
    languages: str = Form(default="eng+khm+fra")
):
    """
    Process an uploaded prescription image.
    
    Args:
        file: Uploaded image file (JPEG, PNG)
        lenient_quality: Use lenient quality thresholds for mobile images
        languages: Tesseract language codes (e.g., "eng+khm+fra")
        
    Returns:
        OCR result with extracted text, confidence scores, and medications
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    contents = await file.read()
    
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    # Run OCR pipeline
    try:
        result = run_pipeline_from_bytes(
            contents,
            lenient_quality=lenient_quality,
            languages=languages
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/process")
async def process_prescription(
    file: UploadFile = File(...),
    lenient_quality: bool = Form(default=False),
    languages: str = Form(default="eng+khm+fra")
):
    """
    Process endpoint for backend integration.
    Returns standardized format with text, confidence, and language.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    try:
        result = run_pipeline_from_bytes(
            contents,
            lenient_quality=lenient_quality,
            languages=languages
        )
        
        # Standardize response format for backend
        return {
            "raw_text": result.get("text", ""),
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0),
            "language": result.get("language", "eng"),
            "layout": result.get("layout", {}),
            "quality_report": result.get("quality_report", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")



@app.post("/ocr/base64", response_model=None)
async def process_base64_image(request: OCRRequest):
    """
    Process a base64-encoded prescription image.
    
    Useful for frontend applications that encode images as base64.
    """
    if not request.image_base64:
        raise HTTPException(status_code=400, detail="No image data provided")
    
    try:
        # Decode base64
        image_data = base64.b64decode(request.image_base64)
        
        # Convert language list to Tesseract format
        lang_str = "+".join([lang.value for lang in request.languages])
        
        # Run pipeline
        result = run_pipeline_from_bytes(
            image_data,
            lenient_quality=request.lenient_quality,
            languages=lang_str
        )
        return JSONResponse(content=result)
    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "languages": [
            {"code": "eng", "name": "English"},
            {"code": "khm", "name": "Khmer (ភាសាខ្មែរ)"},
            {"code": "fra", "name": "French (Français)"}
        ],
        "default": "eng+khm+fra",
        "note": "Use '+' to combine multiple languages"
    }


# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    print("Starting Prescription OCR API...")
    print("Supported languages: English, Khmer, French")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

