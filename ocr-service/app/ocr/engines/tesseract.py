"""
Tesseract OCR Engine
Extracts RAW text with bounding boxes and confidence scores
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
    Run Tesseract OCR on an image
    
    Args:
        image: Preprocessed image (numpy array)
        languages: Language string (e.g., "khm+eng+fra")
        oem: OCR Engine Mode (0-3)
        psm: Page Segmentation Mode (0-13)
        user_words_path: Path to user words file
        
    Returns:
        Dictionary containing OCR data with text, confidence, and positions
    """
    # Use settings defaults if not provided
    lang = languages or settings.OCR_LANGUAGES
    engine_mode = oem if oem is not None else settings.OCR_OEM
    page_seg_mode = psm if psm is not None else settings.OCR_PSM
    user_words = user_words_path or settings.USER_WORDS_PATH
    
    # Build config string
    config_parts = [f"--oem {engine_mode}", f"--psm {page_seg_mode}"]
    
    # Add user words if available
    if user_words:
        config_parts.append(f"--user-words {user_words}")
    
    config = " ".join(config_parts)
    
    logger.info(f"Running OCR with lang={lang}, config={config}")
    
    try:
        # Get detailed OCR data with bounding boxes
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=Output.DICT,
            config=config
        )
        
        logger.info(f"OCR completed. Found {len(data['text'])} elements")
        
        return data
        
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        raise


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
