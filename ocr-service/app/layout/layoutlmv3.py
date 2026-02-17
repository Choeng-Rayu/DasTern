"""
LayoutLMv3 - Document Structure Understanding
Responsibility: Classify blocks (header, medicine list, dosage, notes)
NEVER does OCR - only understands structure

Uses heuristic-based classification initially, with LayoutLMv3 integration planned.
"""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Classification patterns for prescription documents
HEADER_PATTERNS = [
    r"hospital|clinic|medical|center|មន្ទីរពេទ្យ|hôpital",
    r"prescription|វេជ្ជបញ្ជា|ordonnance",
    r"patient|ឈ្មោះ|nom",
    r"date|កាលបរិច្ឆេទ",
    r"doctor|វេជ្ជបណ្ឌិត|médecin",
]

TABLE_HEADER_PATTERNS = [
    r"ល\.រ|no\.|#|seq",
    r"ឈ្មោះថ្នាំ|medicine|médicament|drug",
    r"ចំនួន|qty|quantity|quantité",
    r"morning|ព្រឹក|matin",
    r"noon|ថ្ងៃ|midi",
    r"afternoon|ល្ងាច|après-midi",
    r"evening|យប់|soir",
]

MEDICATION_PATTERNS = [
    r"\d+\s*(mg|ml|g|mcg|iu)",  # Dosage strength
    r"(tablet|capsule|syrup|injection|cream|គ្រាប់|ថ្នាំទឹក)",
    r"(paracetamol|amoxicillin|ibuprofen|omeprazole|metformin)",
]

DOSAGE_PATTERNS = [
    r"\d+\s*x\s*\d+",  # e.g., 1x3, 2x2
    r"\d+\s*(tabs?|caps?|ml)",  # e.g., 2 tabs
    r"(morning|noon|evening|night|ព្រឹក|ថ្ងៃ|ល្ងាច|យប់)",
]

FOOTER_PATTERNS = [
    r"signature|ហត្ថលេខា",
    r"note|remarks|หมายเหตุ",
    r"follow.?up|next\s*visit",
]


def _matches_pattern(text: str, patterns: List[str]) -> bool:
    """Check if text matches any of the given patterns."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


def _is_in_top_region(box: Dict[str, int], img_height: int) -> bool:
    """Check if block is in top 20% of image (header region)."""
    if not img_height:
        return False
    return box.get("y1", 0) < img_height * 0.2


def _is_in_bottom_region(box: Dict[str, int], img_height: int) -> bool:
    """Check if block is in bottom 15% of image (footer region)."""
    if not img_height:
        return False
    return box.get("y2", 0) > img_height * 0.85


def _is_table_row(block: Dict[str, Any], all_blocks: List[Dict[str, Any]]) -> bool:
    """
    Detect if block is part of a table row.
    Tables have multiple aligned blocks in the same Y region.
    """
    y1 = block["box"]["y1"]
    y2 = block["box"]["y2"]
    y_center = (y1 + y2) // 2
    y_threshold = (y2 - y1) // 2  # Half the block height

    # Count blocks at same Y level
    blocks_at_level = 0
    for b in all_blocks:
        if b is block:
            continue
        b_center = (b["box"]["y1"] + b["box"]["y2"]) // 2
        if abs(b_center - y_center) < y_threshold:
            blocks_at_level += 1

    # If 3+ blocks at same level, likely a table row
    return blocks_at_level >= 2


def classify_layout(
    ocr_blocks: List[Dict[str, Any]],
    img_height: int = None,
    img_width: int = None
) -> List[Dict[str, Any]]:
    """
    Classify document structure using heuristic rules.

    Args:
        ocr_blocks: Blocks with text and bounding boxes
        img_height: Image height for position-based classification
        img_width: Image width for position-based classification

    Returns:
        Same blocks with block_type classification added
    """
    if not ocr_blocks:
        return []

    # Estimate image dimensions if not provided
    if not img_height and ocr_blocks:
        img_height = max(b["box"].get("y2", 0) for b in ocr_blocks) + 50
    if not img_width and ocr_blocks:
        img_width = max(b["box"].get("x2", 0) for b in ocr_blocks) + 50

    classified_blocks = []

    for block in ocr_blocks:
        text = block.get("text", "")
        box = block.get("box", {})

        # Initialize block type
        block_type = "body"  # Default

        # Position-based classification
        if _is_in_top_region(box, img_height):
            if _matches_pattern(text, HEADER_PATTERNS):
                block_type = "header"
            elif _matches_pattern(text, TABLE_HEADER_PATTERNS):
                block_type = "table_header"

        elif _is_in_bottom_region(box, img_height):
            if _matches_pattern(text, FOOTER_PATTERNS):
                block_type = "footer"

        # Content-based classification (overrides position if strong match)
        if _matches_pattern(text, TABLE_HEADER_PATTERNS):
            block_type = "table_header"
        elif _matches_pattern(text, MEDICATION_PATTERNS):
            block_type = "medication"
        elif _matches_pattern(text, DOSAGE_PATTERNS):
            block_type = "dosage"

        # Check for table structure
        if _is_table_row(block, ocr_blocks) and block_type == "body":
            block_type = "table_row"

        # Update block with classification
        classified_block = block.copy()
        classified_block["block_type"] = block_type
        classified_blocks.append(classified_block)

    logger.info(f"Classified {len(classified_blocks)} blocks")
    return classified_blocks


def detect_table_structure(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect and extract table structure from classified blocks.

    Args:
        blocks: Classified OCR blocks

    Returns:
        Table structure with headers and rows
    """
    table_blocks = [b for b in blocks if b.get("block_type") in ("table_header", "table_row")]

    if not table_blocks:
        return {"has_table": False}

    # Group by Y coordinate (rows)
    rows = []
    current_row = []
    last_y = None
    y_threshold = 30  # Pixels

    # Sort by Y then X
    sorted_blocks = sorted(table_blocks, key=lambda b: (b["box"]["y1"], b["box"]["x1"]))

    for block in sorted_blocks:
        y = block["box"]["y1"]

        if last_y is None or abs(y - last_y) > y_threshold:
            if current_row:
                rows.append(current_row)
            current_row = [block]
            last_y = y
        else:
            current_row.append(block)

    if current_row:
        rows.append(current_row)

    # Extract text from rows
    header_row = []
    data_rows = []

    for i, row in enumerate(rows):
        row_texts = [b["text"] for b in sorted(row, key=lambda b: b["box"]["x1"])]
        if i == 0 and any(b.get("block_type") == "table_header" for b in row):
            header_row = row_texts
        else:
            data_rows.append(row_texts)

    return {
        "has_table": True,
        "headers": header_row,
        "rows": data_rows,
        "row_count": len(data_rows),
        "col_count": len(header_row) if header_row else max(len(r) for r in data_rows) if data_rows else 0
    }
