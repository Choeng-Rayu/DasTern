"""
Multi-Language OCR Engine using Tesseract
Supports: Khmer (khm), English (eng), French (fra)

Tesseract language codes:
- khm = Khmer
- eng = English
- fra = French
"""

import cv2
import numpy as np
import pytesseract
from typing import List, Tuple, Any, Dict
import logging

logger = logging.getLogger(__name__)

# Tesseract language string for multi-language OCR
# Format: "lang1+lang2+lang3" - Tesseract will try all languages
TESSERACT_LANGS = "khm+eng+fra"


class MultiLangOCR:
    """
    Multi-language OCR using Tesseract.
    Recognizes Khmer, English, and French text simultaneously.
    """

    def __init__(self, langs: str = TESSERACT_LANGS):
        """
        Initialize OCR engine.

        Args:
            langs: Tesseract language string (e.g., "khm+eng+fra")
        """
        self.langs = langs
        logger.info(f"Initialized MultiLangOCR with languages: {langs}")

        # Verify Tesseract languages are installed
        try:
            available = pytesseract.get_languages()
            logger.info(f"Available Tesseract languages: {available}")

            for lang in langs.split('+'):
                if lang not in available:
                    logger.warning(f"Language '{lang}' not installed in Tesseract!")
        except Exception as e:
            logger.warning(f"Could not check Tesseract languages: {e}")

    def ocr(self, img_path: str, cls: bool = True) -> List[List[Any]]:
        """
        Run OCR on image with multi-language support.

        Args:
            img_path: Path to image file
            cls: Unused (for PaddleOCR compatibility)

        Returns:
            List of [bbox, (text, confidence)] results
        """
        try:
            # Read image
            if isinstance(img_path, str):
                image = cv2.imread(img_path)
            else:
                image = img_path

            if image is None:
                logger.error(f"Could not read image: {img_path}")
                return []

            # Convert to RGB for Tesseract
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Run OCR with multi-language support
            logger.info(f"Running Tesseract OCR with langs={self.langs}")
            data = pytesseract.image_to_data(
                rgb_image,
                lang=self.langs,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Assume uniform block of text
            )

            results = []
            n_boxes = len(data['level'])

            for i in range(n_boxes):
                conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0

                if conf > 20:  # Lower threshold to catch more text
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    text = data['text'][i].strip()

                    if text:  # Only include non-empty text
                        # Create bbox in PaddleOCR format
                        bbox = [
                            [x, y],
                            [x + w, y],
                            [x + w, y + h],
                            [x, y + h]
                        ]

                        confidence = float(conf) / 100.0
                        results.append([bbox, (text, confidence)])

            logger.info(f"OCR extracted {len(results)} text blocks")
            return results

        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []


# Global OCR instance
_ocr_engine = None


def get_ocr_engine() -> MultiLangOCR:
    """Get or create OCR engine instance with multi-language support."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = MultiLangOCR(langs=TESSERACT_LANGS)
    return _ocr_engine

def detect_text_language(text: str) -> str:
    """
    Detect the language of a text block based on character analysis.

    Returns:
        'kh' for Khmer, 'fr' for French, 'en' for English, 'mixed' for mixed
    """
    if not text:
        return "unknown"

    khmer_count = 0
    latin_count = 0
    french_chars = set('àâäéèêëïîôùûüçÀÂÄÉÈÊËÏÎÔÙÛÜÇœŒæÆ')
    french_count = 0

    for char in text:
        code = ord(char)
        # Khmer Unicode range: U+1780 to U+17FF
        if 0x1780 <= code <= 0x17FF:
            khmer_count += 1
        elif char.isalpha():
            latin_count += 1
            if char in french_chars:
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


def extract_text_blocks(image_path: str) -> List[Dict]:
    """
    Extract text blocks from image using multi-language OCR.

    Returns:
        List of text blocks with:
        - text: The recognized text
        - confidence: OCR confidence (0-1)
        - bbox: Bounding box {x1, y1, x2, y2}
        - language: Detected language (kh, en, fr, mixed)
    """
    try:
        ocr = get_ocr_engine()
        results = ocr.ocr(image_path, cls=True)

        blocks = []
        for idx, result in enumerate(results):
            if result and len(result) == 2:
                bbox, (text, confidence) = result

                # Convert bbox to simple format
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]

                # Detect language of this text block
                lang = detect_text_language(text)

                block = {
                    'text': text,
                    'confidence': confidence,
                    'bbox': {
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2)
                    },
                    'language': lang,
                    'line_number': idx
                }
                blocks.append(block)

        # Log language distribution
        lang_counts = {}
        for b in blocks:
            lang = b.get('language', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        logger.info(f"Extracted {len(blocks)} blocks. Languages: {lang_counts}")

        return blocks

    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []
