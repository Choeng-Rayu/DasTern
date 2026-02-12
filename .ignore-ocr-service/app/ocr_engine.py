"""
Multi-Language OCR Engine Module

Tesseract-based OCR with intelligent language detection.
Supports: English, Khmer, French (prescription languages).
"""

import pytesseract
import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
from enum import Enum


class Language(str, Enum):
    ENGLISH = "eng"
    KHMER = "khm"
    FRENCH = "fra"
    ENGLISH_FRENCH = "eng+fra"
    ALL = "eng+khm+fra"


# Khmer Unicode range
KHMER_START = 0x1780  # ក
KHMER_END = 0x17FF    # ៿


def detect_language_hint(text: str) -> Language:
    """
    Detect likely language from text sample.
    Used to optimize subsequent OCR passes.
    """
    if not text:
        return Language.ALL
    
    khmer_count = 0
    latin_count = 0
    
    for char in text:
        code = ord(char)
        if KHMER_START <= code <= KHMER_END:
            khmer_count += 1
        elif char.isalpha() and code < 128:
            latin_count += 1
    
    total = khmer_count + latin_count
    if total == 0:
        return Language.ALL
    
    khmer_ratio = khmer_count / total
    
    if khmer_ratio > 0.3:
        return Language.KHMER
    elif khmer_ratio > 0:
        return Language.ALL  # Mixed content
    else:
        return Language.ENGLISH_FRENCH


def has_khmer(text: str) -> bool:
    """Check if text contains Khmer characters."""
    return any(KHMER_START <= ord(c) <= KHMER_END for c in text)


def has_french_chars(text: str) -> bool:
    """Check for French-specific characters."""
    french_chars = set("àâäéèêëïîôùûüçœæÀÂÄÉÈÊËÏÎÔÙÛÜÇŒÆ")
    return any(c in french_chars for c in text)


def ocr(img: np.ndarray, lang: str = "eng+khm+fra", psm: int = 6, oem: int = 1) -> str:
    """
    Perform OCR on image region.
    
    Args:
        img: Preprocessed image (grayscale or binary)
        lang: Tesseract language code(s)
        psm: Page Segmentation Mode
             3 = Fully automatic page segmentation
             6 = Assume uniform block of text
             7 = Single text line
             11 = Sparse text
             12 = Sparse text with OSD
        oem: OCR Engine Mode
             0 = Legacy only
             1 = LSTM only
             2 = Legacy + LSTM
             3 = Default
             
    Returns:
        Extracted text
    """
    config = f"--oem {oem} --psm {psm}"
    
    try:
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        return text.strip()
    except pytesseract.TesseractError as e:
        print(f"OCR Error: {e}")
        return ""


def ocr_with_confidence(img: np.ndarray, lang: str = "eng+khm+fra", psm: int = 6) -> Dict:
    """
    Perform OCR and return detailed results with confidence scores.
    """
    config = f"--oem 1 --psm {psm}"
    
    try:
        data = pytesseract.image_to_data(img, lang=lang, config=config, output_type=pytesseract.Output.DICT)
        
        words = []
        total_conf = 0
        count = 0
        
        for i, text in enumerate(data["text"]):
            if text.strip():
                conf = int(data["conf"][i])
                if conf > 0:
                    words.append({
                        "text": text,
                        "confidence": conf,
                        "box": (data["left"][i], data["top"][i], 
                               data["width"][i], data["height"][i])
                    })
                    total_conf += conf
                    count += 1
        
        full_text = " ".join(w["text"] for w in words)
        avg_conf = total_conf / count if count > 0 else 0
        
        return {
            "text": full_text,
            "confidence": avg_conf,
            "words": words,
            "word_count": count
        }
    except pytesseract.TesseractError as e:
        return {"text": "", "confidence": 0, "words": [], "word_count": 0, "error": str(e)}


def ocr_multi_pass(img: np.ndarray) -> Dict:
    """
    Multi-pass OCR strategy for mixed-language prescriptions.
    First pass detects language, second pass optimizes for detected language.
    """
    # First pass: quick scan with all languages
    initial = ocr(img, lang="eng+khm+fra", psm=6)
    
    # Detect primary language
    detected_lang = detect_language_hint(initial)
    
    # Second pass: optimized for detected language
    if detected_lang == Language.KHMER:
        # Khmer-optimized settings
        optimized = ocr(img, lang="khm+eng", psm=6)
    elif detected_lang == Language.ENGLISH_FRENCH:
        # Latin script optimization
        optimized = ocr(img, lang="eng+fra", psm=6)
    else:
        optimized = initial
    
    return {
        "text": optimized,
        "detected_language": detected_lang.value,
        "initial_text": initial
    }


def ocr_region(img: np.ndarray, box: Tuple[int, int, int, int], lang: str = "eng+khm+fra") -> Dict:
    """
    OCR a specific region of the image.
    """
    x, y, w, h = box
    
    # Extract region with small padding
    pad = 5
    y1 = max(0, y - pad)
    y2 = min(img.shape[0], y + h + pad)
    x1 = max(0, x - pad)
    x2 = min(img.shape[1], x + w + pad)
    
    crop = img[y1:y2, x1:x2]
    
    if crop.size == 0:
        return {"text": "", "confidence": 0, "box": box}
    
    result = ocr_with_confidence(crop, lang=lang)
    result["box"] = box
    
    return result

