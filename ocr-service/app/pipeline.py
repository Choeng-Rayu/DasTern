"""
OCR Pipeline Orchestration - Heart of OCR Service
Coordinates all OCR processing steps

This is the main entry point for OCR processing that:
1. Runs multi-language OCR with PaddleOCR (supports Khmer, English, French)
2. Classifies document layout with LayoutLMv3
3. Groups blocks into logical rows
4. Extracts key-value pairs and table data
5. Applies rule-based corrections
6. Calculates confidence scores
"""

import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Use PaddleOCR with multi-language support (Khmer, English, French)
from .ocr.paddle_engine import extract_text_blocks
logger.info("Using PaddleOCR with multi-language support (Khmer, English, French)")

from .layout.layoutlmv3 import classify_layout, detect_table_structure
from .layout.grouping import group_blocks, group_medication_rows
from .layout.key_value import extract_key_values, extract_medications_from_table
from .rules.medical_terms import fix_terms, normalize_strength, normalize_drug_name
from .rules.khmer_fix import fix_khmer, convert_khmer_digits
from .confidence import calculate_document_confidence


def process_image(image_path: str) -> Dict[str, Any]:
    """
    Complete OCR pipeline for prescription image.

    Steps:
    1. Extract text with PaddleOCR (multi-language)
    2. Classify layout with LayoutLMv3
    3. Group related blocks
    4. Extract key-value pairs
    5. Apply rule-based corrections
    6. Calculate confidence scores

    Args:
        image_path: Path to prescription image

    Returns:
        Structured OCR result with all metadata
    """
    logger.info(f"Processing image: {image_path}")

    # Validate input
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Step 1: Run OCR with multi-language support
    logger.info("Step 1: Running multi-language OCR (Khmer, English, French)...")
    try:
        raw_blocks = extract_text_blocks(image_path)
        # Detect primary language from block analysis
        primary_language = _detect_primary_language(raw_blocks) if raw_blocks else "en"
        logger.info(f"Detected {len(raw_blocks)} blocks, primary language: {primary_language}")
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raw_blocks = []
        primary_language = "en"

    if not raw_blocks:
        return _create_empty_result(image_path)

    # Step 2: Skip layout classification for now (use raw blocks)
    logger.info("Step 2: Using raw blocks...")
    classified_blocks = raw_blocks

    # Skip table detection for now
    table_data = []

    # Step 3: Skip grouping for now
    logger.info("Step 3: Using individual blocks...")
    grouped_blocks = classified_blocks

    # Step 4: Apply text corrections if available
    logger.info("Step 4: Applying text corrections...")
    try:
        from .rules.medical_terms import fix_terms
        from .rules.khmer_fix import fix_khmer
        
        for block in grouped_blocks:
            original_text = block.get("text", "")

            # Apply Khmer fixes first
            corrected_text = fix_khmer(original_text)

            # Then apply medical term fixes
            corrected_text = fix_terms(corrected_text)

            # Convert Khmer digits to Arabic
            corrected_text = convert_khmer_digits(corrected_text)

            block["text"] = corrected_text
            block["original_text"] = original_text
    except ImportError:
        # If correction modules don't exist, skip corrections
        logger.warning("Text correction modules not available, using raw OCR text")
        pass

    # Step 5: Extract structured data (simplified)
    logger.info("Step 5: Creating basic structured data...")
    structured_data = {
        "medications": [],
        "patient_info": {},
        "doctor_info": {},
        "pharmacy_info": {}
    }

    # Step 6: Calculate basic confidence
    logger.info("Step 6: Calculating confidence...")
    try:
        confidence_report = calculate_document_confidence(
            blocks=grouped_blocks,
            medications=structured_data.get("medications", [])
        )
    except Exception as e:
        # Basic confidence calculation fallback
        logger.warning(f"Confidence calculation failed: {e}, using fallback")
        if grouped_blocks:
            total_conf = sum(block.get("confidence", 0.0) if isinstance(block, dict) else 0.0 for block in grouped_blocks)
            avg_conf = total_conf / len(grouped_blocks)
        else:
            avg_conf = 0.0
        confidence_report = {
            "overall_confidence": avg_conf,
            "confidence_level": "medium" if avg_conf > 0.5 else "low"
        }

    #  Build final result
    result = _build_result(
        image_path=image_path,
        blocks=grouped_blocks,
        structured_data=structured_data,
        table_data={},  # Empty dict instead of list
        primary_language=primary_language,
        confidence_report=confidence_report
    )

    logger.info(f"Processing complete. Confidence: {confidence_report['overall_confidence']:.2%}")
    return result


def _create_empty_result(image_path: str) -> Dict[str, Any]:
    """Create empty result for failed OCR."""
    return {
        "success": False,
        "image_path": image_path,
        "raw_text": "",
        "blocks": [],
        "structured_data": None,
        "overall_confidence": 0.0,
        "needs_manual_review": True,
        "error": "No text detected in image"
    }


def _normalize_medications(medications: List[Dict]) -> List[Dict[str, Any]]:
    """Normalize extracted medications with proper formatting."""
    normalized = []

    for med in medications:
        name = med.get("name", "")

        # Normalize drug name
        normalized_name, name_conf = normalize_drug_name(name)

        # Normalize strength
        strength = med.get("strength", "")
        if strength:
            strength = normalize_strength(strength)

        normalized.append({
            "sequence": med.get("sequence", len(normalized) + 1),
            "name": normalized_name,
            "original_name": name,
            "strength": strength,
            "quantity": med.get("quantity"),
            "quantity_unit": med.get("quantity_unit", "tablets"),
            "dosage_schedule": med.get("dosage_schedule", {}),
            "instructions": med.get("instructions"),
            "confidence": name_conf * med.get("confidence", 1.0),
        })

    return normalized


def _extract_medications_from_rows(med_rows: List[Dict]) -> List[Dict[str, Any]]:
    """Extract medications from grouped medication rows."""
    medications = []

    for row in med_rows:
        blocks = row.get("blocks", [])
        if not blocks:
            continue

        # Combine text from all blocks
        combined_text = " ".join(b.get("text", "") for b in blocks)

        # Try to parse medication info
        med = {
            "sequence": row.get("sequence", len(medications) + 1),
            "name": combined_text.split()[0] if combined_text else "",
            "raw_text": combined_text,
            "dosage_schedule": {},
            "confidence": sum(b.get("confidence", 0) for b in blocks) / len(blocks) if blocks else 0
        }

        medications.append(med)

    return medications


def _build_result(
    image_path: str,
    blocks: List[Dict],
    structured_data: Dict,
    table_data: Dict,
    primary_language: str,
    confidence_report: Dict
) -> Dict[str, Any]:
    """Build the final OCR result dictionary."""

    # Combine all text
    raw_text = "\n".join(b.get("text", "") for b in blocks)

    # Map language string to enum
    language_map = {"en": "en", "kh": "kh", "fr": "fr", "mixed": "mixed"}
    language = language_map.get(primary_language, "unknown")

    return {
        "success": True,
        "image_path": image_path,
        "raw_text": raw_text,
        "blocks": blocks,
        "block_count": len(blocks),
        "primary_language": language,
        "structured_data": {
            "patient_name": structured_data.get("patient_name"),
            "patient_age": structured_data.get("patient_age"),
            "patient_gender": structured_data.get("patient_gender"),
            "hospital_name": structured_data.get("hospital_name"),
            "prescription_number": structured_data.get("prescription_number"),
            "diagnosis": structured_data.get("diagnosis"),
            "date": structured_data.get("date"),
            "doctor_name": structured_data.get("doctor_name"),
            "medications": structured_data.get("medications", []),
        },
        "table_detected": table_data.get("has_table", False),
        "table_data": table_data if table_data.get("has_table") else None,
        "overall_confidence": confidence_report.get("overall_confidence", 0.0),
        "confidence_level": confidence_report.get("confidence_level", "critical"),
        "needs_manual_review": confidence_report.get("needs_review", True),
        "review_reasons": confidence_report.get("review_reasons", []),
        "low_confidence_blocks": confidence_report.get("low_confidence_blocks", []),
    }


def process_image_simple(image_path: str) -> List[Dict[str, Any]]:
    """
    Simplified OCR pipeline returning just blocks with corrections.
    Useful for debugging and simpler use cases.

    Args:
        image_path: Path to prescription image

    Returns:
        List of OCR blocks with text corrections applied
    """
    # Run OCR using our mock
    blocks = extract_text_blocks(image_path)

    # Apply basic corrections if available
    try:
        from .rules.medical_terms import fix_terms
        from .rules.khmer_fix import fix_khmer
        
        for block in blocks:
            block["text"] = fix_terms(block["text"])
            block["text"] = fix_khmer(block["text"])
    except ImportError:
        # If correction modules don't exist, just return raw blocks
        pass

    return blocks
