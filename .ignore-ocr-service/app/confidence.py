"""
Confidence Scoring Module

Evaluates OCR result quality for:
- User warnings
- Manual review triggers
- Quality metrics
"""

from typing import Dict, List, Tuple
import re


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using character-level comparison.
    Used to measure OCR correction impact.
    """
    if not text1 and not text2:
        return 1.0
    if not text1 or not text2:
        return 0.0
    
    # Simple Levenshtein-based ratio
    len1, len2 = len(text1), len(text2)
    max_len = max(len1, len2)
    
    if max_len == 0:
        return 1.0
    
    # Count matching characters (order-aware)
    matches = 0
    for i, c1 in enumerate(text1):
        if i < len2 and text1[i] == text2[i]:
            matches += 1
    
    return matches / max_len


def score_text_quality(text: str) -> float:
    """
    Score the quality of extracted text.
    Returns value between 0.0 and 1.0.
    """
    if not text or not text.strip():
        return 0.0
    
    score = 1.0
    
    # Penalize very short text
    if len(text) < 10:
        score *= 0.5
    
    # Penalize excessive special characters
    special_ratio = len(re.findall(r'[^a-zA-Z0-9\s\u1780-\u17FF]', text)) / len(text)
    if special_ratio > 0.3:
        score *= 0.7
    
    # Penalize excessive numbers without letters
    if re.match(r'^[\d\s]+$', text):
        score *= 0.6
    
    # Penalize repeated characters
    if re.search(r'(.)\1{4,}', text):
        score *= 0.8
    
    # Bonus for recognizable patterns
    if re.search(r'\d+\s*(mg|ml|mcg|g)\b', text, re.IGNORECASE):
        score = min(1.0, score * 1.1)
    
    return round(score, 2)


def score_ocr_confidence(raw: str, corrected: str, tesseract_conf: float = None) -> float:
    """
    Calculate overall confidence score for OCR result.
    
    Args:
        raw: Raw OCR output
        corrected: Post-correction text
        tesseract_conf: Optional Tesseract confidence score
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    if not raw and not corrected:
        return 0.0
    
    # Base score from text quality
    quality_score = score_text_quality(corrected if corrected else raw)
    
    # Similarity between raw and corrected
    # High similarity = OCR was good, low = lots of corrections needed
    if raw and corrected:
        similarity = calculate_text_similarity(raw, corrected)
        # We want moderate corrections, not too much or too little
        if similarity < 0.3:
            # Too many corrections - unreliable
            correction_factor = 0.5
        elif similarity > 0.95:
            # Almost no corrections - good OCR
            correction_factor = 1.0
        else:
            # Moderate corrections - expected
            correction_factor = 0.8
    else:
        correction_factor = 0.7
    
    # Incorporate Tesseract confidence if available
    if tesseract_conf is not None:
        tesseract_factor = tesseract_conf / 100.0
    else:
        tesseract_factor = 0.7  # Default assumption
    
    # Weighted combination
    final_score = (quality_score * 0.4 + correction_factor * 0.3 + tesseract_factor * 0.3)
    
    return round(max(0.0, min(1.0, final_score)), 2)


def score(text: str, original: str) -> float:
    """
    Simple confidence score based on text length difference.
    Backward-compatible function.
    """
    if not text:
        return 0.0
    if not original:
        return 0.6
    
    diff = abs(len(text) - len(original))
    base_score = max(0.6, 1 - diff / max(len(original), 1))
    
    return round(base_score, 2)


def needs_manual_review(confidence: float, threshold: float = 0.6) -> bool:
    """Check if result needs manual review based on confidence."""
    return confidence < threshold


def calculate_region_confidences(regions: List[Dict]) -> List[Dict]:
    """
    Calculate confidence scores for all regions.
    """
    for region in regions:
        raw = region.get("raw", "")
        final = region.get("final", "")
        tesseract_conf = region.get("tesseract_confidence")
        
        conf = score_ocr_confidence(raw, final, tesseract_conf)
        region["confidence"] = conf
        region["needs_review"] = needs_manual_review(conf)
    
    return regions


def calculate_document_confidence(regions: List[Dict]) -> Dict:
    """
    Calculate overall document confidence from region scores.
    """
    if not regions:
        return {
            "overall_confidence": 0.0,
            "needs_review": True,
            "review_regions": []
        }
    
    confidences = [r.get("confidence", 0.5) for r in regions]
    avg_conf = sum(confidences) / len(confidences)
    min_conf = min(confidences)
    
    # Document confidence is weighted average with penalty for low regions
    overall = avg_conf * 0.7 + min_conf * 0.3
    
    review_regions = [
        i for i, r in enumerate(regions) 
        if r.get("needs_review", False)
    ]
    
    return {
        "overall_confidence": round(overall, 2),
        "region_confidences": confidences,
        "needs_review": overall < 0.7 or len(review_regions) > 0,
        "review_regions": review_regions
    }

