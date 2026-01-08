"""
Rule-Based Post-Processing Module

Cleans and normalizes OCR output after AI correction.
Handles: whitespace, medication formats, units, common patterns.
"""

import re
from typing import Dict, List, Optional


def clean_whitespace(text: str) -> str:
    """Normalize all whitespace to single spaces."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_units(text: str) -> str:
    """
    Normalize medical units to standard format.
    Examples: 500 mg -> 500mg, 10 ml -> 10ml
    """
    # Common unit patterns
    units = ['mg', 'ml', 'mcg', 'g', 'kg', 'iu', 'mm', 'cm']
    
    for unit in units:
        # Handle space before unit
        text = re.sub(rf'\s+({unit})\b', rf'\1', text, flags=re.IGNORECASE)
        # Handle space after number
        text = re.sub(rf'(\d)\s+({unit})\b', rf'\1\2', text, flags=re.IGNORECASE)
    
    return text


def normalize_dosage(text: str) -> str:
    """
    Standardize dosage expressions.
    Examples: 2 x daily -> twice daily, 1x/day -> once daily
    """
    replacements = {
        r'\b1\s*x\s*(per\s*)?(day|daily)\b': 'once daily',
        r'\b2\s*x\s*(per\s*)?(day|daily)\b': 'twice daily',
        r'\b3\s*x\s*(per\s*)?(day|daily)\b': 'three times daily',
        r'\b4\s*x\s*(per\s*)?(day|daily)\b': 'four times daily',
        r'\bqd\b': 'once daily',
        r'\bbid\b': 'twice daily',
        r'\btid\b': 'three times daily',
        r'\bqid\b': 'four times daily',
        r'\bprn\b': 'as needed',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def fix_common_ocr_errors(text: str) -> str:
    """
    Fix common OCR misrecognitions.
    """
    corrections = {
        r'\bl\b(?=\d)': '1',  # Lowercase L before digit -> 1
        r'(?<=\d)l\b': '1',   # Lowercase L after digit -> 1
        r'\bO(?=\d)': '0',    # O before digit -> 0
        r'(?<=\d)O\b': '0',   # O after digit -> 0
        r'\brng\b': 'mg',     # Common mg misread
        r'\bmq\b': 'mg',
        r'\brnl\b': 'ml',     # Common ml misread
        r'\btabtet\b': 'tablet',
        r'\bcapsute\b': 'capsule',
    }
    
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def normalize_punctuation(text: str) -> str:
    """Fix punctuation issues."""
    # Remove duplicate punctuation
    text = re.sub(r'([.,;:])\1+', r'\1', text)
    # Add space after punctuation if missing
    text = re.sub(r'([.,;:])(?=[A-Za-z])', r'\1 ', text)
    # Remove space before punctuation
    text = re.sub(r'\s+([.,;:])', r'\1', text)
    return text


def clean_khmer_text(text: str) -> str:
    """
    Special cleaning for Khmer script.
    Handles Khmer-specific spacing and character issues.
    """
    # Khmer uses zero-width joiners - normalize these
    text = re.sub(r'\u200B+', '', text)  # Zero-width space
    text = re.sub(r'\u200C+', '', text)  # Zero-width non-joiner
    text = re.sub(r'\u200D+', '', text)  # Zero-width joiner
    
    # Remove orphan diacritics
    text = re.sub(r'[\u17C1-\u17C5](?=\s|$)', '', text)
    
    return text


def clean_french_text(text: str) -> str:
    """
    Special cleaning for French text.
    Handles accented characters and French punctuation.
    """
    # French uses non-breaking space before certain punctuation
    text = re.sub(r'\s+([?!;:])', r' \1', text)
    
    return text


def extract_medication_info(text: str) -> List[Dict]:
    """
    Attempt to extract structured medication information.
    """
    medications = []
    
    # Pattern: medication name + dosage + frequency
    pattern = r'([A-Za-z]+(?:\s+[A-Za-z]+)?)\s*(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g)\s*[,\-]?\s*(.*?)(?:\.|$)'
    
    matches = re.finditer(pattern, text, re.IGNORECASE)
    
    for match in matches:
        medications.append({
            "name": match.group(1).strip(),
            "dosage": f"{match.group(2)}{match.group(3).lower()}",
            "instructions": match.group(4).strip() if match.group(4) else ""
        })
    
    return medications


def clean(text: str, language: str = "eng") -> str:
    """
    Full post-processing pipeline.
    
    Args:
        text: AI-corrected OCR text
        language: Primary language (eng, khm, fra)
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Basic cleaning
    text = clean_whitespace(text)
    text = normalize_punctuation(text)
    
    # Fix common OCR errors
    text = fix_common_ocr_errors(text)
    
    # Language-specific cleaning
    if language == "khm":
        text = clean_khmer_text(text)
    elif language == "fra":
        text = clean_french_text(text)
    
    # Medical-specific normalization
    text = normalize_units(text)
    text = normalize_dosage(text)
    
    # Final whitespace cleanup
    text = clean_whitespace(text)
    
    return text


def postprocess_region(region: Dict) -> Dict:
    """
    Post-process a single region result.
    """
    raw_text = region.get("raw", "")
    ai_text = region.get("ai_corrected", raw_text)
    language = region.get("language", "eng")
    
    cleaned = clean(ai_text, language)
    
    region["final"] = cleaned
    region["medications"] = extract_medication_info(cleaned)
    
    return region

