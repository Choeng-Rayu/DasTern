"""
RapidOCR Engine - PaddleOCR-compatible implementation
Uses RapidOCR (ONNX Runtime) which supports Python 3.14+
Compatible with PaddleOCR API
"""

import logging
from typing import List, Dict, Any
import numpy as np
import cv2

logger = logging.getLogger(__name__)

# Global OCR instance
_ocr_engine = None


def _get_ocr_engine():
    """Get or create RapidOCR engine (PaddleOCR compatible)"""
    global _ocr_engine
    
    if _ocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            logger.info("Initializing RapidOCR engine (PaddleOCR models)")
            _ocr_engine = RapidOCR()
            logger.info("RapidOCR engine initialized successfully")
        except ImportError:
            logger.error("RapidOCR not installed. Install with: pip install rapidocr-onnxruntime")
            raise RuntimeError("RapidOCR not available")
    
    return _ocr_engine


def extract_text_blocks(image_path: str, lang: str = "en") -> List[Dict[str, Any]]:
    """
    Extract text blocks from image using RapidOCR.
    Returns format compatible with original PaddleOCR output.
    
    Args:
        image_path: Path to image file
        lang: Language code (en, kh, fr, mixed)
        
    Returns:
        List of text blocks with bbox, text, and confidence
    """
    try:
        ocr = _get_ocr_engine()
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return []
        
        img_height, img_width = image.shape[:2]
        
        # Run OCR - RapidOCR returns (result, elapsed_time)
        result, elapse = ocr(image_path)
        
        if not result:
            logger.warning(f"No text detected in image: {image_path}")
            return []
        
        blocks = []
        for idx, item in enumerate(result):
            # RapidOCR format: [bbox, text, confidence]
            # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            bbox, text, confidence = item
            
            if not text or not text.strip():
                continue
            
            # Normalize bbox to rectangular format
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            
            x1 = max(0, int(min(x_coords)))
            y1 = max(0, int(min(y_coords)))
            x2 = min(img_width, int(max(x_coords)))
            y2 = min(img_height, int(max(y_coords)))
            
            # Calculate center point
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Detect language (simple heuristic)
            detected_lang = _detect_text_language(text)
            
            block = {
                "block_id": idx,
                "text": text.strip(),
                "confidence": float(confidence),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "center_x": center_x,
                    "center_y": center_y
                },
                "bbox_polygon": bbox,  # Original polygon format
                "language": detected_lang,
                "block_type": "text"  # Default type
            }
            
            blocks.append(block)
        
        logger.info(f"Extracted {len(blocks)} text blocks from {image_path}")
        return blocks
        
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def _detect_text_language(text: str) -> str:
    """
    Detect primary language of text based on character analysis.
    """
    if not text:
        return "unknown"
    
    khmer_count = 0
    latin_count = 0
    french_chars = set('àâäéèêëïîôùûüç')
    french_count = 0
    
    for char in text:
        code = ord(char)
        # Khmer Unicode range: U+1780 to U+17FF
        if 0x1780 <= code <= 0x17FF:
            khmer_count += 1
        elif char.isalpha() and code < 128:
            latin_count += 1
            if char.lower() in french_chars:
                french_count += 1
    
    total_chars = khmer_count + latin_count
    if total_chars == 0:
        return "unknown"
    
    # Determine dominant language
    if khmer_count > total_chars * 0.3:
        return "kh"
    elif french_count > 0 and latin_count > 0:
        return "fr"
    elif latin_count > 0:
        return "en"
    
    return "unknown"


def detect_primary_language(blocks: List[Dict[str, Any]]) -> str:
    """
    Detect the primary language across all blocks.
    """
    lang_counts = {"en": 0, "kh": 0, "fr": 0, "unknown": 0}
    
    for block in blocks:
        lang = block.get("language", "unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    # Return the most common language
    primary_lang = max(lang_counts, key=lang_counts.get)
    return primary_lang if primary_lang != "unknown" else "en"
