"""
API Routes for OCR Service

Endpoints:
- POST /ocr - Process prescription image
- POST /ocr/analyze - Quality analysis only
- GET /health - Health check
- GET /info - Service info
"""

from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.core.pipeline import OCRPipeline
from app.core.exceptions import OCRServiceError
from app.core.logging import get_logger, set_request_id
from app.core.config import settings
from app.schemas.responses import OCRResponse, QualityMetrics, HealthResponse, ErrorResponse
from app.schemas.requests import OCRRequest

logger = get_logger(__name__)

router = APIRouter(tags=["OCR"])

# Pipeline instance (singleton)
_pipeline: Optional[OCRPipeline] = None


def get_pipeline() -> OCRPipeline:
    """Get or create pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = OCRPipeline()
    return _pipeline


@router.post(
    "/ocr",
    response_model=OCRResponse,
    summary="Process prescription image",
    description="Upload a prescription image for OCR processing. Returns structured JSON with bounding boxes."
)
async def process_ocr(
    file: UploadFile = File(..., description="Prescription image file"),
    languages: Optional[str] = Form(
        default=None,
        description="Override languages (e.g., 'eng+khm+fra')"
    ),
    skip_enhancement: bool = Form(
        default=False,
        description="Skip preprocessing if image is clean"
    ),
    pipeline: OCRPipeline = Depends(get_pipeline)
):
    """
    Process a prescription image through the OCR pipeline.
    
    Returns structured JSON with:
    - Bounding boxes for all text
    - Confidence scores
    - Layout block information (tables, headers, etc.)
    - Quality metrics
    """
    request_id = set_request_id()
    logger.info(f"OCR request received: {file.filename}")
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Process through pipeline
        result = await pipeline.process(
            image_bytes=image_bytes,
            filename=file.filename or "image.jpg",
            languages=languages,
            skip_enhancement=skip_enhancement
        )
        
        return result
        
    except OCRServiceError as e:
        logger.error(f"OCR error: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": str(e)
            }
        )


@router.post(
    "/ocr/analyze",
    response_model=QualityMetrics,
    summary="Analyze image quality",
    description="Analyze image quality without full OCR processing."
)
async def analyze_quality(
    file: UploadFile = File(..., description="Image file to analyze"),
    pipeline: OCRPipeline = Depends(get_pipeline)
):
    """
    Analyze image quality to preview before full OCR.
    
    Returns:
    - Blur level
    - Contrast level
    - Skew angle
    - Recommendations
    """
    logger.info(f"Quality analysis request: {file.filename}")
    
    try:
        image_bytes = await file.read()
        
        result = await pipeline.analyze_quality_only(
            image_bytes=image_bytes,
            filename=file.filename or "image.jpg"
        )
        
        return result
        
    except OCRServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check service health and Tesseract availability."
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
    - Service status
    - Tesseract availability
    - Available languages
    """
    try:
        import pytesseract
        
        tesseract_available = True
        languages = []
        
        try:
            languages = pytesseract.get_languages()
        except Exception:
            tesseract_available = False
        
        return HealthResponse(
            status="healthy" if tesseract_available else "degraded",
            tesseract_available=tesseract_available,
            languages_available=languages,
            version="1.0.0"
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            tesseract_available=False,
            languages_available=[],
            version="1.0.0"
        )


@router.get(
    "/info",
    summary="Service information",
    description="Get service configuration and capabilities."
)
async def service_info():
    """
    Get service information.
    """
    return {
        "service": "OCR Service",
        "version": "1.0.0",
        "description": "Layer-by-layer OCR for Cambodian prescriptions",
        "supported_languages": settings.default_languages.split("+"),
        "supported_formats": settings.supported_formats,
        "min_dpi": settings.min_dpi,
        "active_model": settings.active_model,
        "layers": [
            "1. Image Intake & Validation",
            "2. Quality Analysis",
            "3. Preprocessing & Enhancement",
            "4. Layout Analysis",
            "5. OCR Extraction (Tesseract)",
            "6. Post-processing",
            "7. JSON Builder"
        ]
    }
