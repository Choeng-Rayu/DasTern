"""
Enhanced Tesseract OCR Engine for Cambodian Prescriptions
Optimized for mixed-language prescription OCR with improved accuracy
Languages: Khmer (khm) + English (eng) + French (fra)
"""
import pytesseract
from pytesseract import Output
import numpy as np
from typing import Dict, List, Any, Optional
from ...core.config import settings
from ...core.logger import logger


def run_ocr(
    image: np.ndarray,
    languages: Optional[str] = None,
    oem: Optional[int] = None,
    psm: Optional[int] = None,
    user_words_path: Optional[str] = None
) -> Dict[str, List]:
    """
    Run enhanced Tesseract OCR for Cambodian prescriptions
    
    Args:
        image: Preprocessed image (numpy array)
        languages: Language string (e.g., "khm+eng+fra")
        oem: OCR Engine Mode (0-3)
        psm: Page Segmentation Mode (0-13)
        user_words_path: Path to user words file
        
    Returns:
        Dictionary containing OCR data with text, confidence, and positions
    """
    # Import enhanced OCR function
    from .enhanced_tesseract import run_enhanced_ocr
    
    logger.info("Using enhanced OCR for prescription processing")
    
    return run_enhanced_ocr(image, languages, oem, psm, user_words_path)


def get_full_text(
    image: np.ndarray,
    languages: Optional[str] = None
) -> str:
    """
    Get simple text extraction (without bounding boxes)
    
    Args:
        image: Input image
        languages: Language string
        
    Returns:
        Extracted text as string
    """
    lang = languages or settings.OCR_LANGUAGES
    
    text = pytesseract.image_to_string(
        image,
        lang=lang,
        config=f"--oem {settings.OCR_OEM} --psm {settings.OCR_PSM}"
    )
    
    return text.strip()


def get_available_languages() -> List[str]:
    """
    Get list of available Tesseract languages
    
    Returns:
        List of installed language codes
    """
    try:
        langs = pytesseract.get_languages()
        return langs
    except Exception as e:
        logger.error(f"Failed to get languages: {str(e)}")
        return []


def check_tesseract_installed() -> bool:
    """
    Check if Tesseract is properly installed
    
    Returns:
        True if Tesseract is available
    """
    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract not found: {str(e)}")
        return False
