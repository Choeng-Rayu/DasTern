"""
Confidence Scoring
Responsibility: Calculate and expose uncertainty
Medical system MUST show confidence levels
"""

import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Confidence thresholds for medical documents
THRESHOLDS = {
    "high": 0.90,       # Very confident - safe to use
    "medium": 0.75,     # Needs review but usable
    "low": 0.60,        # Requires manual verification
    "critical": 0.40,   # Likely incorrect - must review
}

# Block type importance weights (higher = more critical)
BLOCK_WEIGHTS = {
    "medication": 1.5,      # Most critical - drug names
    "dosage": 1.4,          # Very important - dosage info
    "patient_info": 1.2,    # Important - patient details
    "table_row": 1.1,       # Important - medication table
    "header": 0.9,          # Less critical
    "body": 1.0,            # Default
    "footer": 0.7,          # Least critical
    "unknown": 1.0,
}


def calculate_confidence(blocks: List[Dict[str, Any]]) -> float:
    """
    Calculate overall confidence score from OCR blocks.
    Uses weighted average based on block importance.

    Args:
        blocks: OCR blocks with individual confidence scores

    Returns:
        Weighted average confidence score (0.0 to 1.0)
    """
    if not blocks:
        return 0.0

    total_weighted_conf = 0.0
    total_weight = 0.0

    for block in blocks:
        conf = block.get("confidence", 0.0)
        block_type = block.get("block_type", "unknown")
        weight = BLOCK_WEIGHTS.get(block_type, 1.0)

        total_weighted_conf += conf * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return total_weighted_conf / total_weight


def get_low_confidence_blocks(
    blocks: List[Dict[str, Any]],
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Identify blocks with low confidence that need review.

    Args:
        blocks: OCR blocks
        threshold: Minimum acceptable confidence

    Returns:
        List of blocks below threshold, sorted by confidence (lowest first)
    """
    low_conf_blocks = []

    for idx, block in enumerate(blocks):
        conf = block.get("confidence", 0.0)
        if conf < threshold:
            low_conf_blocks.append({
                "index": idx,
                "text": block.get("text", ""),
                "confidence": conf,
                "block_type": block.get("block_type", "unknown"),
                "box": block.get("box", {}),
            })

    # Sort by confidence (lowest first)
    low_conf_blocks.sort(key=lambda x: x["confidence"])

    return low_conf_blocks


def get_confidence_level(confidence: float) -> str:
    """
    Convert confidence score to categorical level.

    Args:
        confidence: Confidence score (0.0 to 1.0)

    Returns:
        Confidence level string
    """
    if confidence >= THRESHOLDS["high"]:
        return "high"
    elif confidence >= THRESHOLDS["medium"]:
        return "medium"
    elif confidence >= THRESHOLDS["low"]:
        return "low"
    else:
        return "critical"


def needs_manual_review(
    blocks: List[Dict[str, Any]],
    threshold: float = 0.7
) -> Tuple[bool, List[str]]:
    """
    Determine if document needs manual review.

    Args:
        blocks: OCR blocks
        threshold: Confidence threshold

    Returns:
        Tuple of (needs_review: bool, reasons: List[str])
    """
    reasons = []

    # Calculate overall confidence
    overall_conf = calculate_confidence(blocks)
    if overall_conf < THRESHOLDS["medium"]:
        reasons.append(f"Overall confidence too low: {overall_conf:.2%}")

    # Check for low confidence blocks
    low_conf = get_low_confidence_blocks(blocks, threshold)
    if len(low_conf) > len(blocks) * 0.2:  # More than 20% low confidence
        reasons.append(f"{len(low_conf)} blocks have low confidence")

    # Check for critical medication/dosage blocks
    for block in blocks:
        block_type = block.get("block_type", "")
        conf = block.get("confidence", 0.0)

        if block_type in ("medication", "dosage") and conf < THRESHOLDS["medium"]:
            reasons.append(f"Critical block '{block.get('text', '')[:30]}...' has low confidence: {conf:.2%}")

    return len(reasons) > 0, reasons


def calculate_document_confidence(
    blocks: List[Dict[str, Any]],
    medications: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive document confidence metrics.

    Args:
        blocks: OCR blocks
        medications: Extracted medications

    Returns:
        Comprehensive confidence report
    """
    report = {
        "overall_confidence": 0.0,
        "confidence_level": "critical",
        "needs_review": True,
        "review_reasons": [],
        "block_metrics": {
            "total": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "critical_confidence": 0,
        },
        "medication_confidence": 0.0,
        "low_confidence_blocks": [],
    }

    if not blocks:
        return report

    # Calculate overall confidence
    report["overall_confidence"] = calculate_confidence(blocks)
    report["confidence_level"] = get_confidence_level(report["overall_confidence"])

    # Block metrics
    report["block_metrics"]["total"] = len(blocks)
    for block in blocks:
        conf = block.get("confidence", 0.0)
        level = get_confidence_level(conf)
        report["block_metrics"][f"{level}_confidence"] += 1

    # Low confidence blocks
    report["low_confidence_blocks"] = get_low_confidence_blocks(blocks)

    # Check if review needed
    needs_review, reasons = needs_manual_review(blocks)
    report["needs_review"] = needs_review
    report["review_reasons"] = reasons

    # Medication-specific confidence
    if medications:
        med_confidences = [m.get("confidence", 0.0) for m in medications if m.get("confidence")]
        if med_confidences:
            report["medication_confidence"] = sum(med_confidences) / len(med_confidences)

    return report


def score_extraction_quality(
    extracted: Dict[str, Any],
    expected_fields: List[str] = None
) -> float:
    """
    Score the quality of structured extraction.

    Args:
        extracted: Extracted structured data
        expected_fields: List of expected field names

    Returns:
        Quality score (0.0 to 1.0)
    """
    if expected_fields is None:
        expected_fields = [
            "hospital_name", "patient_name", "date",
            "medications", "doctor_name"
        ]

    if not extracted:
        return 0.0

    filled_count = 0
    for field in expected_fields:
        value = extracted.get(field)
        if value and (not isinstance(value, list) or len(value) > 0):
            filled_count += 1

    return filled_count / len(expected_fields) if expected_fields else 0.0
