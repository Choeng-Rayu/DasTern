"""
OCR API Routes
Endpoints for OCR processing
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.logger import logger
from ..models.raw_ocr import OCRResponse, HealthResponse
from ..ocr.engines.tesseract import check_tesseract_installed, get_available_languages
from ..ocr.extractors.raw_text import extract_raw_ocr
from ..ocr.parsers.tesseract_parser import calculate_page_stats
from ..utils.image import load_image_from_bytes, get_image_info


router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service status and Tesseract availability
    """
    tesseract_ok = check_tesseract_installed()
    languages = get_available_languages() if tesseract_ok else []
    
    return HealthResponse(
        status="healthy" if tesseract_ok else "degraded",
        tesseract_installed=tesseract_ok,
        available_languages=languages,
        version=settings.APP_VERSION
    )


@router.post("/extract", response_model=OCRResponse)
async def extract_text(
    file: UploadFile = File(..., description="Image file to process"),
    apply_preprocessing: bool = Form(default=True, description="Apply image preprocessing"),
    languages: Optional[str] = Form(default=None, description="OCR languages (e.g., 'khm+eng+fra')"),
    include_low_confidence: bool = Form(default=True, description="Include low confidence results"),
    include_stats: bool = Form(default=True, description="Include statistics in response"),
):
    """
    Extract raw OCR text from an image
    
    This endpoint:
    - Accepts an image file
    - Extracts text using Tesseract OCR
    - Returns raw OCR results with bounding boxes and confidence
    
    NO interpretation, fixing, or guessing is done.
    The raw OCR output is preserved exactly as detected.
    """
    logger.info(f"OCR request received: {file.filename}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Expected image/*"
        )
    
    try:
        # Read and decode image
        contents = await file.read()
        
        # Check file size
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size_mb:.2f}MB. Max: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        image = load_image_from_bytes(contents)
        image_info = get_image_info(image)
        logger.info(f"Image loaded: {image_info}")
        
        # Extract OCR
        result = extract_raw_ocr(
            image,
            apply_preprocessing=apply_preprocessing,
            languages=languages,
            include_low_confidence=include_low_confidence
        )
        
        # Calculate stats if requested
        stats = None
        if include_stats:
            stats = calculate_page_stats(result["raw"])
            stats["image_width"] = image_info["width"]
            stats["image_height"] = image_info["height"]
        
        return OCRResponse(
            success=True,
            page=1,
            raw=result["raw"],
            stats=stats,
            languages_used=result["languages_used"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}", exc_info=True)
        return OCRResponse(
            success=False,
            page=1,
            raw=[],
            error=str(e)
        )


@router.post("/extract-and-save")
async def extract_and_save(
    file: UploadFile = File(..., description="Image file to process"),
    output_name: Optional[str] = Form(default=None, description="Output file name (without extension)"),
    apply_preprocessing: bool = Form(default=True),
    languages: Optional[str] = Form(default=None),
):
    """
    Extract OCR and save result to JSON file
    
    Saves result as: tesseract_result_{number}.json
    """
    logger.info(f"OCR extract-and-save request: {file.filename}")
    
    try:
        # Read and decode image
        contents = await file.read()
        image = load_image_from_bytes(contents)
        
        # Extract OCR
        result = extract_raw_ocr(
            image,
            apply_preprocessing=apply_preprocessing,
            languages=languages,
            include_low_confidence=True
        )
        
        # Calculate stats
        stats = calculate_page_stats(result["raw"])
        image_info = get_image_info(image)
        stats["image_width"] = image_info["width"]
        stats["image_height"] = image_info["height"]
        
        # Determine output path
        results_dir = settings.RESULTS_DIR
        results_dir.mkdir(parents=True, exist_ok=True)
        
        if output_name:
            output_path = results_dir / f"{output_name}.json"
        else:
            # Find next test number
            existing = list(results_dir.glob("tesseract_result_*.json"))
            test_num = len(existing) + 1
            output_path = results_dir / f"tesseract_result_{test_num}.json"
        
        # Prepare output
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "source_file": file.filename,
            "page": 1,
            "raw": result["raw"],
            "stats": stats,
            "languages_used": result["languages_used"]
        }
        
        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_path}")
        
        return JSONResponse({
            "success": True,
            "message": f"Results saved to {output_path.name}",
            "output_path": str(output_path),
            "total_elements": len(result["raw"]),
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Extract and save failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_languages():
    """
    Get available OCR languages
    """
    languages = get_available_languages()
    
    # Check for required languages
    required = ["eng", "fra", "khm"]
    missing = [lang for lang in required if lang not in languages]
    
    return {
        "available": languages,
        "required": required,
        "missing": missing,
        "all_required_installed": len(missing) == 0
    }
