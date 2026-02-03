"""
Raw Text Extractor
Combines preprocessing and OCR engine to extract text
"""
import numpy as np
from typing import Dict, List, Any, Optional
from ..preprocess.opencv import preprocess_for_ocr
from ..engines.tesseract import run_ocr, get_full_text
from ..parsers.tesseract_parser import parse_ocr_data
from ...core.logger import logger


def extract_raw_ocr(
    image: np.ndarray,
    apply_preprocessing: bool = True,
    languages: Optional[str] = None,
    include_low_confidence: bool = True
) -> Dict[str, Any]:
    """
    Extract raw OCR data from image
    
    This is the main extraction pipeline:
    1. Preprocess image
    2. Run OCR
    3. Parse results
    
    Args:
        image: Input image (BGR format)
        apply_preprocessing: Whether to preprocess
        languages: OCR languages
        include_low_confidence: Include low confidence results
        
    Returns:
        Dictionary with raw OCR results
    """
    logger.info("Starting raw OCR extraction")
    
    # Step 1: Preprocess
    processed_image = preprocess_for_ocr(image, apply_preprocessing)
    
    # Step 2: Run OCR
    ocr_data = run_ocr(processed_image, languages=languages)
    
    # Step 3: Parse results
    parsed_results = parse_ocr_data(ocr_data, include_low_confidence)
    
    logger.info(f"Extracted {len(parsed_results)} text elements")
    
    return {
        "raw": parsed_results,
        "total_elements": len(parsed_results),
        "languages_used": languages or "khm+eng+fra"
    }


def extract_text_only(
    image: np.ndarray,
    apply_preprocessing: bool = True,
    languages: Optional[str] = None
) -> str:
    """
    Extract just the text (no bounding boxes)
    
    Args:
        image: Input image
        apply_preprocessing: Whether to preprocess
        languages: OCR languages
        
    Returns:
        Extracted text as string
    """
    processed_image = preprocess_for_ocr(image, apply_preprocessing)
    return get_full_text(processed_image, languages)
