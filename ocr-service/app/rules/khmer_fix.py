"""
Khmer Language Specific Fixes
Responsibility: Handle Khmer OCR errors and normalization

Khmer Unicode range: U+1780 to U+17FF
Includes special handling for:
- Consonants (ក-ហ)
- Vowels (ា-ៗ)
- Diacritics
- Khmer digits (០-៩)
"""

import re
import unicodedata
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Khmer Unicode constants
KHMER_START = 0x1780  # ក
KHMER_END = 0x17FF    # ៿

# Common OCR confusions in Khmer script
KHMER_FIXES: Dict[str, str] = {
    # Character confusions (similar looking characters)
    "រា": "រ៉ា",  # Missing diacritic
    "កា": "ក៉ា",

    # Common medical terms in Khmer
    "គ្រប់": "គ្រាប់",    # "tablets" - common misspelling
    "ព្រិក": "ព្រឹក",    # "morning"
    "លង្ាច": "ល្ងាច",   # "afternoon"
    "យប": "យប់",       # "night"
    "ថ្ង": "ថ្ងៃ",      # "day/noon"

    # Hospital/medical terms
    "មន្ដីរពេទ្យ": "មន្ទីរពេទ្យ",  # "hospital"
    "វេជ្ជបណ្ឌិដ": "វេជ្ជបណ្ឌិត",  # "doctor"

    # Common prescription words
    "ថ្នាម": "ថ្នាំ",    # "medicine"
    "ជំង": "ជំងឺ",      # "disease"
    "អ្នកជំង": "អ្នកជំងឺ",  # "patient"
}

# Khmer digits mapping
KHMER_DIGITS = "០១២៣៤៥៦៧៨៩"
ARABIC_DIGITS = "0123456789"

# Common prescription column headers in Khmer
KHMER_HEADERS: Dict[str, str] = {
    "ល.រ": "sequence",         # No./Sequence
    "ឈ្មោះថ្នាំ": "medicine",    # Medicine name
    "ចំនួន": "quantity",        # Quantity
    "ព្រឹក": "morning",         # Morning
    "ថ្ងៃ": "noon",             # Noon/Midday
    "ល្ងាច": "afternoon",       # Afternoon
    "យប់": "night",            # Night
}


def is_khmer_text(text: str) -> bool:
    """
    Check if text contains Khmer characters.

    Args:
        text: Input text

    Returns:
        True if text contains Khmer characters
    """
    for char in text:
        if KHMER_START <= ord(char) <= KHMER_END:
            return True
    return False


def get_khmer_ratio(text: str) -> float:
    """
    Calculate the ratio of Khmer characters in text.

    Args:
        text: Input text

    Returns:
        Ratio of Khmer characters (0.0 to 1.0)
    """
    if not text:
        return 0.0

    khmer_count = sum(1 for c in text if KHMER_START <= ord(c) <= KHMER_END)
    total_alpha = sum(1 for c in text if c.isalpha() or KHMER_START <= ord(c) <= KHMER_END)

    return khmer_count / total_alpha if total_alpha > 0 else 0.0


def normalize_khmer_unicode(text: str) -> str:
    """
    Normalize Khmer Unicode text to NFC form.
    Ensures consistent character representation.

    Args:
        text: Input text with potential Unicode variations

    Returns:
        Normalized Unicode text
    """
    return unicodedata.normalize("NFC", text)


def fix_khmer(text: str) -> str:
    """
    Fix common Khmer OCR mistakes.

    Args:
        text: Raw Khmer OCR text

    Returns:
        Corrected Khmer text
    """
    if not text:
        return text

    # First, normalize Unicode
    result = normalize_khmer_unicode(text)

    # Apply known corrections
    for wrong, correct in KHMER_FIXES.items():
        result = result.replace(wrong, correct)

    # Fix spacing around Khmer text
    result = fix_khmer_spacing(result)

    return result


def fix_khmer_spacing(text: str) -> str:
    """
    Fix common spacing issues in Khmer text.
    Khmer doesn't use spaces between words typically.

    Args:
        text: Input Khmer text

    Returns:
        Text with corrected spacing
    """
    # Remove extra spaces between Khmer characters
    # But preserve spaces between Khmer and Latin text
    result = text

    # Don't remove all spaces, just reduce multiple spaces to one
    result = re.sub(r"([^\s])\s{2,}([^\s])", r"\1 \2", result)

    return result


def convert_khmer_digits(text: str) -> str:
    """
    Convert Khmer digits to Arabic numerals.

    Args:
        text: Text with Khmer digits

    Returns:
        Text with Arabic numerals
    """
    result = text
    for khmer, arabic in zip(KHMER_DIGITS, ARABIC_DIGITS):
        result = result.replace(khmer, arabic)
    return result


def convert_to_khmer_digits(text: str) -> str:
    """
    Convert Arabic numerals to Khmer digits.

    Args:
        text: Text with Arabic numerals

    Returns:
        Text with Khmer digits
    """
    result = text
    for arabic, khmer in zip(ARABIC_DIGITS, KHMER_DIGITS):
        result = result.replace(arabic, khmer)
    return result


def extract_khmer_time_slot(text: str) -> str:
    """
    Map Khmer time slot words to English.

    Args:
        text: Khmer time slot text

    Returns:
        English time slot or original text
    """
    text_clean = text.strip()

    for khmer, english in KHMER_HEADERS.items():
        if khmer in text_clean:
            return english

    return text_clean


def split_khmer_latin(text: str) -> List[Dict[str, str]]:
    """
    Split mixed Khmer/Latin text into segments.

    Args:
        text: Mixed text

    Returns:
        List of segments with language tags
    """
    segments = []
    current_segment = ""
    current_lang = None

    for char in text:
        char_code = ord(char)

        if KHMER_START <= char_code <= KHMER_END:
            char_lang = "kh"
        elif char.isalpha():
            char_lang = "latin"
        else:
            # Numbers, punctuation, spaces - keep with current segment
            if current_segment:
                current_segment += char
            continue

        if current_lang is None:
            current_lang = char_lang
            current_segment = char
        elif char_lang == current_lang:
            current_segment += char
        else:
            # Language switch
            if current_segment.strip():
                segments.append({
                    "text": current_segment.strip(),
                    "language": current_lang
                })
            current_segment = char
            current_lang = char_lang

    # Add final segment
    if current_segment.strip():
        segments.append({
            "text": current_segment.strip(),
            "language": current_lang
        })

    return segments


def detect_prescription_language(blocks: List[Dict]) -> str:
    """
    Detect primary language of prescription from OCR blocks.

    Args:
        blocks: List of OCR blocks

    Returns:
        Primary language code ("kh", "en", "fr", "mixed")
    """
    khmer_blocks = 0
    latin_blocks = 0

    for block in blocks:
        text = block.get("text", "")
        ratio = get_khmer_ratio(text)

        if ratio > 0.5:
            khmer_blocks += 1
        elif ratio < 0.1:
            latin_blocks += 1

    total = khmer_blocks + latin_blocks
    if total == 0:
        return "unknown"

    khmer_ratio = khmer_blocks / total

    if khmer_ratio > 0.6:
        return "kh"
    elif khmer_ratio > 0.3:
        return "mixed"
    else:
        return "en"
