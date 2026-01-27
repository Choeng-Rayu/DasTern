"""
PaddleOCR Engine - Text Extraction
Responsibility: Image → raw text + bounding boxes
NO cleanup, NO rules - keep raw OCR output

Uses PaddleOCR standard API with ocr() method
"""

import os
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import cv2

# Initialize logger
logger = logging.getLogger(__name__)

# Global OCR instances - initialized lazily
_ocr_engines: Dict[str, Any] = {}


def _get_ocr_engine(lang: str = "en") -> Any:
    """
    Get or create PaddleOCR engine for specified language.
    Engines are cached for reuse.
    
    Khmer support: PaddleOCR's 'ch' (Chinese) model supports multilingual including Khmer.
    """
    global _ocr_engines

    if lang not in _ocr_engines:
        try:
            from paddleocr import PaddleOCR

            # Language mapping for PaddleOCR
            # 'ch' (Chinese/multilingual) model supports Khmer, English, numbers, and common symbols
            lang_map = {
                "en": "ch",  # Use multilingual model for better support
                "kh": "ch",  # Khmer is supported by Chinese multilingual model
                "fr": "french",  # French specific
                "mixed": "ch",  # Multilingual model handles mixed text best
            }
            paddle_lang = lang_map.get(lang, "ch")

            logger.info(f"Initializing PaddleOCR engine for language: {lang} -> model: {paddle_lang}")
            # PaddleOCR initialization - minimal params for compatibility
            _ocr_engines[lang] = PaddleOCR(lang=paddle_lang)
            logger.info(f"PaddleOCR engine initialized successfully: {lang}")
        except ImportError:
            logger.error("PaddleOCR not installed. Install with: pip install paddleocr")
            raise RuntimeError("PaddleOCR not available")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise

    return _ocr_engines[lang]


def _normalize_bbox(box: List[List[float]], img_width: int, img_height: int) -> Dict[str, int]:
    """
    Normalize PaddleOCR polygon bbox to rectangular format.
    PaddleOCR returns [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
    """
    if not box or len(box) < 4:
        return {"x1": 0, "y1": 0, "x2": 0, "y2": 0}

    # Extract all x and y coordinates
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]

    # Get bounding rectangle
    x1 = max(0, int(min(x_coords)))
    y1 = max(0, int(min(y_coords)))
    x2 = min(img_width, int(max(x_coords)))
    y2 = min(img_height, int(max(y_coords)))

    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


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

    total = khmer_count + latin_count
    if total == 0:
        return "unknown"

    khmer_ratio = khmer_count / total
    french_ratio = french_count / max(1, latin_count)

    if khmer_ratio > 0.3:
        return "kh"
    elif french_ratio > 0.1:
        return "fr"
    elif latin_count > 0:
        return "en"
    return "mixed"


def run_ocr(image_path: str, lang: str = "en") -> List[Dict[str, Any]]:
    """
    Run OCR on image and extract text with bounding boxes.

    Uses PaddleOCR standard ocr() method.

    Args:
        image_path: Path to prescription image
        lang: Target language (en, kh, fr)

    Returns:
        List of blocks with text, bbox, and confidence
    """
    blocks = []

    try:
        # Load image to get dimensions
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return blocks

        img_height, img_width = img.shape[:2]

        # Get OCR engine
        ocr = _get_ocr_engine(lang)

        # Run OCR using PaddleOCR ocr() method
        logger.info(f"Running PaddleOCR on: {image_path}")
        results = ocr.ocr(image_path)

        if not results or not results[0]:
            logger.warning(f"No results from OCR for image: {image_path}")
            return blocks

        # PaddleOCR returns format: [[[bbox, (text, confidence)]...]]
        # results[0] contains list of detected text regions
        for line in results[0]:
            if not line or len(line) < 2:
                continue

            bbox_coords, (text, conf) = line
            
            if not text or not text.strip():
                continue

            # Normalize bounding box
            bbox = _normalize_bbox(bbox_coords, img_width, img_height)

            # Detect language of this block
            block_lang = _detect_text_language(text)

            blocks.append({
                "text": text.strip(),
                "box": bbox,
                "confidence": float(conf),
                "language": block_lang,
                "line_number": len(blocks)
            })

        logger.info(f"OCR extracted {len(blocks)} text blocks from {image_path}")

    except Exception as e:
        logger.error(f"OCR error: {str(e)}")
        raise

    return blocks


def run_ocr_multi_language(image_path: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Run OCR with multi-language support.
    First pass detects language, second pass optimizes for detected language.

    Args:
        image_path: Path to prescription image

    Returns:
        Tuple of (blocks, detected_primary_language)
    """
    # First pass with English (most general)
    initial_blocks = run_ocr(image_path, lang="en")

    if not initial_blocks:
        return [], "unknown"

    # Analyze detected languages
    lang_counts = {"en": 0, "kh": 0, "fr": 0}
    for block in initial_blocks:
        block_lang = block.get("language", "en")
        if block_lang in lang_counts:
            lang_counts[block_lang] += 1

    # Determine primary language
    primary_lang = max(lang_counts, key=lang_counts.get)

    # If significant Khmer or French detected, do second pass
    total_blocks = len(initial_blocks)
    if total_blocks > 0:
        khmer_ratio = lang_counts["kh"] / total_blocks
        french_ratio = lang_counts["fr"] / total_blocks

        if khmer_ratio > 0.3 or french_ratio > 0.3:
            # Second pass with detected language
            second_pass = run_ocr(image_path, lang=primary_lang)
            if second_pass:
                initial_blocks = second_pass

    return initial_blocks, primary_lang


def run_ocr_on_region(
    image: np.ndarray,
    box: Tuple[int, int, int, int],
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Run OCR on a specific region of the image.

    Args:
        image: Image as numpy array
        box: Region coordinates (x, y, w, h)
        lang: Language for OCR

    Returns:
        OCR result for the region
    """
    x, y, w, h = box

    # Extract region with padding
    pad = 5
    y1 = max(0, y - pad)
    y2 = min(image.shape[0], y + h + pad)
    x1 = max(0, x - pad)
    x2 = min(image.shape[1], x + w + pad)

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        return {"text": "", "confidence": 0, "box": box}

    # Save temp file for PaddleOCR
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        cv2.imwrite(tmp.name, crop)
        blocks = run_ocr(tmp.name, lang)

    # Combine results
    if blocks:
        combined_text = " ".join(b["text"] for b in blocks)
        avg_conf = sum(b["confidence"] for b in blocks) / len(blocks)
        return {
            "text": combined_text,
            "confidence": avg_conf,
            "box": {"x1": x, "y1": y, "x2": x + w, "y2": y + h},
            "words": blocks
        }

    return {"text": "", "confidence": 0, "box": box}


# Public API function for pipeline
def extract_text_blocks(image_path: str, lang: str = "mixed") -> List[Dict[str, Any]]:
    """
    Extract text blocks from image with PaddleOCR multi-language support.
    This function is the main entry point used by pipeline.py
    
    Args:
        image_path: Path to image file
        lang: Language hint ('en', 'kh', 'fr', 'mixed')
        
    Returns:
        List of text blocks with text, box, confidence, language
    """
    logger.info(f"Extracting text blocks from {image_path} with lang={lang}")
    
    # Use multi-language detection if lang is 'mixed' or not specified
    if lang == "mixed" or not lang:
        blocks, detected_lang = run_ocr_multi_language(image_path)
        logger.info(f"Detected primary language: {detected_lang}, extracted {len(blocks)} blocks")
        return blocks
    else:
        # Single language mode
        blocks = run_ocr(image_path, lang=lang)
        logger.info(f"Extracted {len(blocks)} blocks with lang={lang}")
        return blocks
