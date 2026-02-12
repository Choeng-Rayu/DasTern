"""
Key-Value Extraction
Responsibility: Detect patterns like Drug→Dosage, Frequency→Duration
Rule-based, not AI
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Khmer dosage column headers
KHMER_TIME_SLOTS = {
    "ព្រឹក": "morning",     # Morning
    "ថ្ងៃ": "noon",         # Noon/Midday
    "ល្ងាច": "afternoon",   # Afternoon/Evening
    "យប់": "night",         # Night
}

# Common dosage patterns
DOSAGE_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg|iu|tab|cap|tablette?s?|capsule?s?|គ្រាប់)",
    r"(\d+)\s*x\s*(\d+)",  # e.g., 1x3
    r"(\d+)\s*/\s*(\d+)\s*/\s*(\d+)",  # e.g., 1/1/1
]

# Quantity patterns
QUANTITY_PATTERNS = [
    r"(\d+)\s*(គ្រាប់|tablets?|caps?|pills?|pcs?|pieces?)",
    r"qty[:\s]*(\d+)",
    r"ចំនួន[:\s]*(\d+)",
]

# Duration patterns
DURATION_PATTERNS = [
    r"(\d+)\s*(days?|weeks?|months?|ថ្ងៃ|សប្តាហ៍)",
    r"for\s+(\d+)\s+(days?|weeks?)",
]


def extract_dosage_from_text(text: str) -> Dict[str, Any]:
    """
    Extract dosage information from text.

    Args:
        text: Text containing dosage info

    Returns:
        Extracted dosage components
    """
    result = {
        "strength": None,
        "quantity": None,
        "schedule": {},
        "duration_days": None,
    }

    # Extract strength (e.g., 10mg, 500mg)
    strength_match = re.search(r"(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg|iu)", text, re.IGNORECASE)
    if strength_match:
        result["strength"] = f"{strength_match.group(1)}{strength_match.group(2).lower()}"

    # Extract quantity
    for pattern in QUANTITY_PATTERNS:
        qty_match = re.search(pattern, text, re.IGNORECASE)
        if qty_match:
            result["quantity"] = int(qty_match.group(1))
            break

    # Extract duration
    for pattern in DURATION_PATTERNS:
        dur_match = re.search(pattern, text, re.IGNORECASE)
        if dur_match:
            duration = int(dur_match.group(1))
            unit = dur_match.group(2).lower()
            if "week" in unit or "សប្តាហ៍" in unit:
                duration *= 7
            elif "month" in unit:
                duration *= 30
            result["duration_days"] = duration
            break

    return result


def extract_schedule_from_row(row_cells: List[str]) -> Dict[str, float]:
    """
    Extract dosage schedule from table row cells.

    Cambodian prescriptions typically have columns for:
    Morning (ព្រឹក), Noon (ថ្ងៃ), Afternoon (ល្ងាច), Night (យប់)

    Args:
        row_cells: List of cell texts from a row

    Returns:
        Schedule dict with time slots and doses
    """
    schedule = {}

    # If we have exactly 4 numeric values at the end, assume they're dosage
    numeric_cells = []
    for cell in row_cells:
        cell = cell.strip()
        # Handle Khmer digits too
        if re.match(r"^[\d៰១២៣៤៥៦៧៨៩\.]+$", cell):
            numeric_cells.append(cell)

    time_slots = ["morning", "noon", "afternoon", "night"]

    # Take last 4 numbers as schedule
    if len(numeric_cells) >= 4:
        for i, slot in enumerate(time_slots):
            if i < len(numeric_cells):
                try:
                    # Convert Khmer digits if needed
                    value = _convert_khmer_digits(numeric_cells[-(4-i)])
                    schedule[slot] = float(value) if value else None
                except (ValueError, IndexError):
                    pass

    return schedule


def _convert_khmer_digits(text: str) -> str:
    """Convert Khmer digits to Arabic numerals."""
    khmer_digits = "០១២៣៤៥៦៧៨៩"
    arabic_digits = "0123456789"

    result = text
    for khmer, arabic in zip(khmer_digits, arabic_digits):
        result = result.replace(khmer, arabic)

    return result


def extract_key_values(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract key-value pairs from structured blocks.

    Args:
        blocks: Grouped OCR blocks

    Returns:
        Dictionary with extracted prescription data
    """
    result = {
        "patient_name": None,
        "patient_age": None,
        "patient_gender": None,
        "hospital_name": None,
        "prescription_number": None,
        "diagnosis": None,
        "date": None,
        "doctor_name": None,
        "medications": [],
    }

    # Key patterns for extraction
    key_patterns = {
        "patient_name": [r"(?:patient|name|ឈ្មោះ)[:\s]*(.+)", r"ឈ្មោះ\s*[:\s]*(.+)"],
        "patient_age": [r"(?:age|អាយុ)[:\s]*(\d+)", r"(\d+)\s*(?:years?|ឆ្នាំ)"],
        "patient_gender": [r"(?:gender|sex|ភេទ)[:\s]*(m|f|male|female|ប្រុស|ស្រី)"],
        "hospital_name": [r"(hospital|clinic|មន្ទីរពេទ្យ).+", r"មន្ទីរពេទ្យ(.+)"],
        "prescription_number": [r"(?:prescription|rx|no\.?|លេខ)[:\s#]*([A-Z0-9]+)"],
        "diagnosis": [r"(?:diagnosis|dx|រោគវិនិច្ឆ័យ)[:\s]*(.+)"],
        "date": [r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})", r"(?:date|កាលបរិច្ឆេទ)[:\s]*(.+)"],
        "doctor_name": [r"(?:doctor|dr\.?|វេជ្ជបណ្ឌិត)[:\s]*(.+)"],
    }

    # Extract header info
    for block in blocks:
        text = block.get("text", "")
        block_type = block.get("block_type", "")

        if block_type in ("header", "patient_info", "doctor_info"):
            for key, patterns in key_patterns.items():
                if result[key] is None:
                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            value = match.group(1).strip()
                            if key == "patient_age":
                                result[key] = int(value)
                            else:
                                result[key] = value
                            break

    return result


def extract_medications_from_table(
    table_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Extract medication list from detected table structure.

    Args:
        table_data: Table structure with headers and rows

    Returns:
        List of extracted medications
    """
    medications = []

    if not table_data.get("has_table"):
        return medications

    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])

    # Determine column indices based on headers
    col_map = _detect_column_mapping(headers)

    for i, row in enumerate(rows):
        if not row:
            continue

        med = {
            "sequence": i + 1,
            "name": None,
            "strength": None,
            "quantity": None,
            "quantity_unit": None,
            "dosage_schedule": {},
            "instructions": None,
        }

        # Extract based on column mapping
        for col_type, col_idx in col_map.items():
            if col_idx < len(row):
                cell_value = row[col_idx].strip()

                if col_type == "name":
                    med["name"] = cell_value
                    # Try to extract strength from name
                    dosage_info = extract_dosage_from_text(cell_value)
                    if dosage_info["strength"]:
                        med["strength"] = dosage_info["strength"]

                elif col_type == "quantity":
                    try:
                        med["quantity"] = int(re.search(r"\d+", cell_value).group())
                    except (AttributeError, ValueError):
                        pass

                elif col_type in ("morning", "noon", "afternoon", "night"):
                    try:
                        value = _convert_khmer_digits(cell_value)
                        if value and value != "-":
                            med["dosage_schedule"][col_type] = float(value)
                    except ValueError:
                        pass

        if med["name"]:
            medications.append(med)

    logger.info(f"Extracted {len(medications)} medications from table")
    return medications


def _detect_column_mapping(headers: List[str]) -> Dict[str, int]:
    """Detect which column contains what type of data."""
    col_map = {}

    header_patterns = {
        "sequence": [r"^(?:no\.?|#|ល\.រ|លេខ)$"],
        "name": [r"(?:medicine|drug|medication|ឈ្មោះថ្នាំ|médicament)"],
        "quantity": [r"(?:qty|quantity|ចំនួន|quantité)"],
        "morning": [r"(?:morning|am|ព្រឹក|matin)"],
        "noon": [r"(?:noon|midday|ថ្ងៃ|midi)"],
        "afternoon": [r"(?:afternoon|pm|ល្ងាច|après)"],
        "night": [r"(?:night|evening|យប់|soir)"],
    }

    for idx, header in enumerate(headers):
        header_lower = header.lower().strip()
        for col_type, patterns in header_patterns.items():
            for pattern in patterns:
                if re.search(pattern, header_lower, re.IGNORECASE):
                    col_map[col_type] = idx
                    break

    # Default: assume first non-number column is name, following numbers are dosage
    if "name" not in col_map and headers:
        for idx, header in enumerate(headers):
            if not re.match(r"^\d+$", header.strip()):
                col_map["name"] = idx
                break

    return col_map
