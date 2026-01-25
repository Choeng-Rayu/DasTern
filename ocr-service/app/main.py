"""
OCR Service API Entry Point
FastAPI application for prescription OCR processing
"""

import os
import uuid
import logging
import tempfile
from typing import Optional, List
from datetime import datetime

import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .pipeline import process_image, process_image_simple
from .confidence import calculate_confidence, get_low_confidence_blocks

# AI LLM Service URL
AI_LLM_SERVICE_URL = os.getenv("AI_LLM_SERVICE_URL", "http://ai-llm-service:8001")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DasTern OCR Service",
    description="Document AI for prescription processing with multi-language support (EN, KH, FR)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

# Temp file directory
TEMP_DIR = tempfile.gettempdir()


class ValidationRequest(BaseModel):
    """Request body for OCR validation"""
    blocks: List[dict]
    threshold: Optional[float] = 0.7


class ValidationResponse(BaseModel):
    """Response for OCR validation"""
    overall_confidence: float
    confidence_level: str
    low_confidence_blocks: List[dict]
    needs_review: bool


def cleanup_temp_file(file_path: str):
    """Background task to clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up temp file {file_path}: {e}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "DasTern OCR Service",
        "status": "ready",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "ocr_engine": "ready",
            "layout_model": "ready",
            "rules_engine": "ready"
        }
    }


@app.post("/ocr", response_model=None)
async def ocr_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Process prescription image with OCR.

    Supports multi-language prescriptions (English, Khmer, French).
    Returns structured OCR result with blocks, layout classification,
    extracted medications, and confidence scores.

    Args:
        file: Uploaded prescription image (JPEG, PNG, BMP, TIFF, WebP)

    Returns:
        Structured OCR result with all metadata
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    image_path = os.path.join(TEMP_DIR, unique_filename)

    try:
        # Save uploaded file temporarily
        contents = await file.read()
        with open(image_path, "wb") as f:
            f.write(contents)

        logger.info(f"Processing file: {file.filename} -> {image_path}")

        # Process through pipeline
        result = process_image(image_path)

        # Add ai_enhanced flag (default to False)
        result["ai_enhanced"] = False

        # Try to enhance with AI (graceful degradation)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                ai_response = await client.post(
                    f"{AI_LLM_SERVICE_URL}/enhance",
                    json={"ocr_data": result}
                )
                if ai_response.status_code == 200:
                    enhanced_data = ai_response.json()
                    if enhanced_data.get("ai_enhanced"):
                        # Merge AI enhancements into result
                        result = enhanced_data.get("data", result)
                        result["ai_enhanced"] = True
                        result["prescription_summary"] = enhanced_data.get("prescription_summary")
                        result["validation"] = enhanced_data.get("validation")
                        logger.info("AI enhancement successful")
                    else:
                        logger.info("AI enhancement returned but not applied")
                else:
                    logger.warning(f"AI service returned status {ai_response.status_code}")
        except httpx.TimeoutException:
            logger.warning("AI enhancement timed out - returning raw OCR data")
        except httpx.ConnectError:
            logger.warning("AI service not available - returning raw OCR data")
        except Exception as e:
            # Do not show error to user, just return raw OCR data
            logger.warning(f"AI enhancement failed (graceful degradation): {e}")

        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, image_path)

        return JSONResponse(content=result)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        # Still try to cleanup
        background_tasks.add_task(cleanup_temp_file, image_path)
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/ocr/simple")
async def ocr_simple_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Simplified OCR endpoint returning just corrected blocks.
    Useful for debugging and simpler use cases.

    Args:
        file: Uploaded prescription image

    Returns:
        List of OCR blocks with text corrections applied
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    unique_filename = f"{uuid.uuid4()}{file_ext}"
    image_path = os.path.join(TEMP_DIR, unique_filename)

    try:
        contents = await file.read()
        with open(image_path, "wb") as f:
            f.write(contents)

        blocks = process_image_simple(image_path)

        background_tasks.add_task(cleanup_temp_file, image_path)

        return {"blocks": blocks, "count": len(blocks)}

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        background_tasks.add_task(cleanup_temp_file, image_path)
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/ocr/validate", response_model=ValidationResponse)
async def validate_ocr(data: ValidationRequest):
    """
    Validate OCR results and return confidence scores.

    Args:
        data: OCR blocks to validate

    Returns:
        Validation results with flagged low-confidence blocks
    """
    blocks = data.blocks
    threshold = data.threshold

    if not blocks:
        return ValidationResponse(
            overall_confidence=0.0,
            confidence_level="critical",
            low_confidence_blocks=[],
            needs_review=True
        )

    # Calculate confidence
    overall_conf = calculate_confidence(blocks)

    # Get low confidence blocks
    low_conf = get_low_confidence_blocks(blocks, threshold)

    # Determine confidence level
    if overall_conf >= 0.90:
        level = "high"
    elif overall_conf >= 0.75:
        level = "medium"
    elif overall_conf >= 0.60:
        level = "low"
    else:
        level = "critical"

    return ValidationResponse(
        overall_confidence=overall_conf,
        confidence_level=level,
        low_confidence_blocks=low_conf,
        needs_review=level in ("low", "critical") or len(low_conf) > 0
    )
