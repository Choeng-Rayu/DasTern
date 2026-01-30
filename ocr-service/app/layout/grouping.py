"""
Block Grouping Logic
Responsibility: Merge nearby blocks, reconstruct medicine rows
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def _calculate_y_overlap(box1: Dict[str, int], box2: Dict[str, int]) -> float:
    """Calculate vertical overlap ratio between two boxes."""
    y1_start, y1_end = box1["y1"], box1["y2"]
    y2_start, y2_end = box2["y1"], box2["y2"]

    overlap_start = max(y1_start, y2_start)
    overlap_end = min(y1_end, y2_end)

    if overlap_end <= overlap_start:
        return 0.0

    overlap_height = overlap_end - overlap_start
    min_height = min(y1_end - y1_start, y2_end - y2_start)

    if min_height <= 0:
        return 0.0

    return overlap_height / min_height


def _get_x_distance(box1: Dict[str, int], box2: Dict[str, int]) -> int:
    """Calculate horizontal distance between two boxes."""
    if box1["x2"] <= box2["x1"]:
        return box2["x1"] - box1["x2"]
    elif box2["x2"] <= box1["x1"]:
        return box1["x1"] - box2["x2"]
    else:
        return 0  # Overlapping


def group_blocks(blocks: List[Dict[str, Any]], y_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Group blocks by Y-axis proximity to reconstruct logical rows.

    Args:
        blocks: OCR blocks with bounding boxes
        y_threshold: Minimum vertical overlap ratio to group (0.0 to 1.0)

    Returns:
        Grouped blocks representing logical rows
    """
    if not blocks:
        return []

    # Sort blocks by Y coordinate first, then X
    sorted_blocks = sorted(blocks, key=lambda b: (b["box"]["y1"], b["box"]["x1"]))

    # Group blocks into rows
    rows = []
    current_row = []

    for block in sorted_blocks:
        if not current_row:
            current_row = [block]
            continue

        # Check if block belongs to current row (sufficient Y overlap)
        belongs_to_row = False
        for row_block in current_row:
            overlap = _calculate_y_overlap(block["box"], row_block["box"])
            if overlap >= y_threshold:
                belongs_to_row = True
                break

        if belongs_to_row:
            current_row.append(block)
        else:
            rows.append(current_row)
            current_row = [block]

    if current_row:
        rows.append(current_row)

    # Assign group IDs and sort each row by X
    grouped_blocks = []
    for group_id, row in enumerate(rows):
        sorted_row = sorted(row, key=lambda b: b["box"]["x1"])
        for block in sorted_row:
            grouped_block = block.copy()
            grouped_block["group_id"] = group_id
            grouped_blocks.append(grouped_block)

    logger.info(f"Grouped {len(blocks)} blocks into {len(rows)} rows")
    return grouped_blocks


def merge_row_text(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge text from blocks in the same row.

    Args:
        blocks: Grouped blocks with group_id

    Returns:
        List of merged row blocks
    """
    if not blocks:
        return []

    # Group by group_id
    rows_dict: Dict[int, List[Dict[str, Any]]] = {}
    for block in blocks:
        group_id = block.get("group_id", 0)
        if group_id not in rows_dict:
            rows_dict[group_id] = []
        rows_dict[group_id].append(block)

    merged_rows = []
    for group_id in sorted(rows_dict.keys()):
        row_blocks = sorted(rows_dict[group_id], key=lambda b: b["box"]["x1"])

        # Merge text with appropriate spacing
        merged_text = ""
        for i, block in enumerate(row_blocks):
            if i > 0:
                # Add space based on X distance
                x_dist = _get_x_distance(row_blocks[i-1]["box"], block["box"])
                avg_char_width = 10  # Approximate
                if x_dist > avg_char_width * 3:
                    merged_text += "\t"  # Tab for large gaps
                else:
                    merged_text += " "
            merged_text += block["text"]

        # Create merged bounding box
        x1 = min(b["box"]["x1"] for b in row_blocks)
        y1 = min(b["box"]["y1"] for b in row_blocks)
        x2 = max(b["box"]["x2"] for b in row_blocks)
        y2 = max(b["box"]["y2"] for b in row_blocks)

        # Average confidence
        avg_conf = sum(b["confidence"] for b in row_blocks) / len(row_blocks)

        merged_rows.append({
            "text": merged_text,
            "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "confidence": avg_conf,
            "group_id": group_id,
            "block_count": len(row_blocks),
            "original_blocks": row_blocks
        })

    return merged_rows


def group_medication_rows(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group blocks specifically for medication table structure.
    Detects numbered rows (1., 2., 3., etc.) and groups related info.

    Args:
        blocks: Classified OCR blocks

    Returns:
        Medication rows with associated dosage info
    """
    import re

    # First, group by Y proximity
    grouped = group_blocks(blocks)

    # Identify medication rows by sequence numbers
    medication_rows = []
    current_med = None

    for block in grouped:
        text = block.get("text", "").strip()

        # Check if this starts a new medication (numbered)
        if re.match(r"^\d+[\.\)\s]", text):
            if current_med:
                medication_rows.append(current_med)
            current_med = {
                "blocks": [block],
                "group_id": block.get("group_id"),
                "sequence": int(re.match(r"^(\d+)", text).group(1))
            }
        elif current_med and block.get("group_id") == current_med.get("group_id"):
            # Same row as current medication
            current_med["blocks"].append(block)
        elif current_med:
            # Check if this is dosage info on next line
            block_type = block.get("block_type", "")
            if block_type in ("dosage", "table_row"):
                current_med["blocks"].append(block)

    if current_med:
        medication_rows.append(current_med)

    logger.info(f"Identified {len(medication_rows)} medication rows")
    return medication_rows
