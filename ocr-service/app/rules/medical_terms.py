"""
Medical Terms Correction
Responsibility: Fix OCR mistakes, normalize spelling
DO NOT hallucinate - only fix known common mistakes
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Common OCR mistakes in medical terms (lowercase keys)
COMMON_FIXES: Dict[str, str] = {
    # Paracetamol variations
    "paracatamol": "paracetamol",
    "paracetomol": "paracetamol",
    "parcetamol": "paracetamol",
    "paracetamo1": "paracetamol",
    "paracetarnol": "paracetamol",

    # Amoxicillin variations
    "amoxicilin": "amoxicillin",
    "amoxicilln": "amoxicillin",
    "amoxiciIlin": "amoxicillin",
    "arnoxicillin": "amoxicillin",
    "amoxycillin": "amoxicillin",

    # Ibuprofen variations
    "lbuprofen": "ibuprofen",
    "ibuproffen": "ibuprofen",
    "ibuprofin": "ibuprofen",
    "ibuprohen": "ibuprofen",

    # Omeprazole variations
    "omeprazol": "omeprazole",
    "omeprazo1e": "omeprazole",
    "orneprazole": "omeprazole",

    # Metformin variations
    "metforrnin": "metformin",
    "metforrnln": "metformin",

    # Common antibiotics
    "azithromycin": "azithromycin",
    "azlthromycin": "azithromycin",
    "ciprofloxacin": "ciprofloxacin",
    "clprofloxacin": "ciprofloxacin",
    "doxycycline": "doxycycline",
    "doxycycllne": "doxycycline",

    # Common medications
    "omeprazoie": "omeprazole",
    "pantoprazole": "pantoprazole",
    "esomeprazole": "esomeprazole",
    "ranitidine": "ranitidine",
    "famotidine": "famotidine",
    "cetirizine": "cetirizine",
    "loratadine": "loratadine",
    "diphenhydramine": "diphenhydramine",
    "chlorpheniramine": "chlorpheniramine",

    # Pain medications
    "diclofenac": "diclofenac",
    "dlclofenac": "diclofenac",
    "naproxen": "naproxen",
    "tramadol": "tramadol",
    "tranadol": "tramadol",

    # Diabetes medications
    "glibenclamide": "glibenclamide",
    "gliclazide": "gliclazide",
    "pioglitazone": "pioglitazone",

    # Blood pressure medications
    "amlodipine": "amlodipine",
    "arnlodipine": "amlodipine",
    "losartan": "losartan",
    "valsartan": "valsartan",
    "enalapril": "enalapril",
    "lisinopril": "lisinopril",

    # Common OCR number/letter confusions
    "0mg": "0mg",  # Keep as is
    "1mg": "1mg",
    "5oomg": "500mg",
    "1oomg": "100mg",
    "2oomg": "200mg",
    "25omg": "250mg",
}

# Unit corrections
UNIT_FIXES: Dict[str, str] = {
    "rng": "mg",
    "rnl": "ml",
    "m9": "mg",
    "m1": "ml",
    "rnq": "mg",
    "mcg": "mcg",
    "µg": "mcg",
    "iu": "IU",
    "lu": "IU",
}

# Frequency/instruction corrections
INSTRUCTION_FIXES: Dict[str, str] = {
    "once daiiy": "once daily",
    "once da1ly": "once daily",
    "twice daiiy": "twice daily",
    "tlmes": "times",
    "t1mes": "times",
    "before meai": "before meal",
    "after meai": "after meal",
    "w1th food": "with food",
}


def fix_terms(text: str) -> str:
    """
    Fix common OCR mistakes in medical terminology.

    Args:
        text: Raw OCR text

    Returns:
        Text with corrections applied
    """
    if not text:
        return text

    result = text
    corrections_made = []

    # Apply word-by-word corrections
    words = result.split()
    fixed_words = []

    for word in words:
        word_lower = word.lower()
        fixed_word = word

        # Check medical term fixes
        if word_lower in COMMON_FIXES:
            # Preserve original case if possible
            fixed_word = _preserve_case(word, COMMON_FIXES[word_lower])
            if fixed_word != word:
                corrections_made.append((word, fixed_word))
        else:
            # Check unit fixes
            for wrong, correct in UNIT_FIXES.items():
                if wrong in word_lower:
                    fixed_word = re.sub(re.escape(wrong), correct, word, flags=re.IGNORECASE)
                    if fixed_word != word:
                        corrections_made.append((word, fixed_word))
                    break

        fixed_words.append(fixed_word)

    result = " ".join(fixed_words)

    # Apply phrase-level fixes
    for wrong, correct in INSTRUCTION_FIXES.items():
        if wrong in result.lower():
            result = re.sub(re.escape(wrong), correct, result, flags=re.IGNORECASE)
            corrections_made.append((wrong, correct))

    if corrections_made:
        logger.debug(f"Applied {len(corrections_made)} corrections: {corrections_made}")

    return result


def _preserve_case(original: str, replacement: str) -> str:
    """
    Preserve the case pattern of original in the replacement.
    """
    if original.isupper():
        return replacement.upper()
    elif original.istitle():
        return replacement.title()
    else:
        return replacement


def normalize_strength(strength: str) -> str:
    """
    Normalize medication strength format.

    Args:
        strength: Raw strength string (e.g., "500 mg", "10MG")

    Returns:
        Normalized strength (e.g., "500mg", "10mg")
    """
    if not strength:
        return strength

    # Remove spaces between number and unit
    result = re.sub(r"(\d+)\s+(mg|ml|g|mcg|iu)", r"\1\2", strength, flags=re.IGNORECASE)

    # Fix unit case
    for wrong, correct in UNIT_FIXES.items():
        result = re.sub(r"\b" + re.escape(wrong) + r"\b", correct, result, flags=re.IGNORECASE)

    # Standardize to lowercase unit (except IU)
    result = re.sub(r"(\d+)(mg|ml|g|mcg)", lambda m: m.group(1) + m.group(2).lower(), result)

    return result


def normalize_drug_name(name: str) -> Tuple[str, float]:
    """
    Normalize drug name and return confidence of correction.

    Args:
        name: Raw drug name

    Returns:
        Tuple of (normalized_name, confidence)
    """
    if not name:
        return name, 0.0

    original = name
    normalized = fix_terms(name)

    # Calculate confidence based on similarity
    if original.lower() == normalized.lower():
        return normalized, 1.0  # No change needed
    else:
        # Some correction was made
        return normalized, 0.9  # High confidence in known corrections


def get_drug_aliases() -> Dict[str, List[str]]:
    """
    Get dictionary of drug names and their common aliases/misspellings.
    Useful for fuzzy matching.
    """
    aliases = {}
    for misspelling, correct in COMMON_FIXES.items():
        if correct not in aliases:
            aliases[correct] = []
        aliases[correct].append(misspelling)
    return aliases
