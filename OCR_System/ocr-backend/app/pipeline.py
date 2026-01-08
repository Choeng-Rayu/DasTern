"""
Main OCR Pipeline Module

Connects all components into a complete prescription OCR system.
Flow: Quality Gate → Preprocessing → Layout → OCR → AI Correction → Post-processing → Output
"""

import cv2
import numpy as np
import time
from typing import Dict, List, Optional, Union

from .quality import quality_check, quality_check_lenient
from .preprocess import preprocess, preprocess_for_khmer
from .layout import extract_regions, merge_overlapping_regions
from .ocr_engine import ocr, ocr_with_confidence, ocr_multi_pass, detect_language_hint
from .ai_corrector import ai_correct, detect_and_correct
from .postprocess import clean, postprocess_region
from .confidence import score_ocr_confidence, calculate_document_confidence, needs_manual_review
from .schemas import build_output


def run_pipeline(
    img: np.ndarray,
    use_ai_correction: bool = True,
    lenient_quality: bool = False,
    languages: str = "eng+khm+fra"
) -> Dict:
    """
    Run the complete OCR pipeline on an image.
    
    Args:
        img: Input image in BGR format (from cv2.imread)
        use_ai_correction: Whether to apply MT5 AI correction
        lenient_quality: Use lenient quality thresholds for mobile images
        languages: Tesseract language codes
        
    Returns:
        Structured OCR result dictionary
    """
    start_time = time.time()
    
    # Step 1: Quality Gate
    if lenient_quality:
        quality_ok, quality_msg, quality_metrics = quality_check_lenient(img)
    else:
        quality_ok, quality_msg, quality_metrics = quality_check(img)
    
    quality_metrics["passed"] = quality_ok
    quality_metrics["message"] = quality_msg
    
    if not quality_ok:
        return build_output(
            regions=[],
            quality_metrics=quality_metrics,
            processing_time=int((time.time() - start_time) * 1000),
            error=quality_msg
        )
    
    # Step 2: Preprocessing
    preprocessed = preprocess(img, apply_deskew=True)
    
    # Also prepare grayscale version for OCR (often works better)
    gray_preprocessed = preprocess(img, apply_deskew=True, return_gray=True)
    
    # Step 3: Layout Analysis
    regions = extract_regions(preprocessed)
    regions = merge_overlapping_regions(regions)
    
    if not regions:
        # Fallback: treat entire image as one region
        h, w = preprocessed.shape[:2]
        regions = [{
            "box": (0, 0, w, h),
            "type": "body",
            "area": w * h
        }]
    
    # Step 4: Region-Based OCR
    results = []
    for region in regions:
        x, y, w, h = region["box"]
        
        # Extract region from both preprocessed versions
        crop_binary = preprocessed[y:y+h, x:x+w]
        crop_gray = gray_preprocessed[y:y+h, x:x+w]
        
        if crop_binary.size == 0:
            continue
        
        # Multi-pass OCR
        ocr_result = ocr_multi_pass(crop_gray)
        raw_text = ocr_result["text"]
        detected_lang = ocr_result["detected_language"]
        
        # Get confidence from Tesseract
        conf_result = ocr_with_confidence(crop_gray, lang=languages)
        tesseract_conf = conf_result.get("confidence", 0)
        
        # Step 5: AI Correction (if enabled)
        if use_ai_correction and raw_text.strip():
            try:
                # Map detected language to correction language
                lang_map = {"khm": "khm", "eng+fra": "eng", "eng+khm+fra": "eng"}
                correction_lang = lang_map.get(detected_lang, "eng")
                ai_corrected = ai_correct(raw_text, correction_lang)
            except Exception as e:
                print(f"AI correction failed: {e}")
                ai_corrected = raw_text
        else:
            ai_corrected = raw_text
        
        # Step 6: Post-processing
        final_text = clean(ai_corrected, language=detected_lang.split("+")[0] if detected_lang else "eng")
        
        # Step 7: Confidence Scoring
        confidence = score_ocr_confidence(raw_text, final_text, tesseract_conf)
        
        results.append({
            "box": region["box"],
            "type": region["type"],
            "raw": raw_text,
            "ai_corrected": ai_corrected,
            "final": final_text,
            "detected_language": detected_lang,
            "tesseract_confidence": tesseract_conf,
            "confidence": confidence,
            "needs_review": needs_manual_review(confidence)
        })
    
    # Calculate overall document confidence
    doc_confidence = calculate_document_confidence(results)
    
    # Build structured output
    processing_time = int((time.time() - start_time) * 1000)
    
    return build_output(
        regions=results,
        quality_metrics=quality_metrics,
        processing_time=processing_time
    )


def run_pipeline_simple(img: np.ndarray, lang: str = "eng+khm+fra") -> str:
    """
    Simplified pipeline that returns just the extracted text.
    Useful for quick testing or simple integrations.
    """
    result = run_pipeline(img, use_ai_correction=True, languages=lang)
    return result.get("full_text", "")


def run_pipeline_from_file(filepath: str, **kwargs) -> Dict:
    """
    Run pipeline from image file path.
    """
    img = cv2.imread(filepath)
    if img is None:
        return build_output(
            regions=[],
            error=f"Failed to load image: {filepath}"
        )
    return run_pipeline(img, **kwargs)


def run_pipeline_from_bytes(image_bytes: bytes, **kwargs) -> Dict:
    """
    Run pipeline from image bytes (e.g., from HTTP upload).
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return build_output(
            regions=[],
            error="Failed to decode image from bytes"
        )
    return run_pipeline(img, **kwargs)

