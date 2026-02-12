"""
AI OCR Corrector Module using MT5-Small

Supports: English, Khmer, French medical prescription text.
Purpose: OCR error correction and normalization (text-only).
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import torch

from .model_loader import get_model

logger = logging.getLogger(__name__)


def _load_prompt(template_name: str) -> str:
    prompt_path = Path(__file__).parent / "prompts" / f"{template_name}.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return ""


def correct_ocr_text(raw_text: str, language: str = "en", context: Optional[Dict] = None) -> Dict:
    """
    Correct OCR text using MT5 model.

    Args:
        raw_text: Raw OCR output
        language: Language code (en, km, fr)
        context: Optional metadata to assist correction

    Returns:
        dict with corrected_text, confidence, language, metadata
    """
    if not raw_text or not raw_text.strip():
        return {
            "corrected_text": "",
            "confidence": 0.0,
            "language": language,
            "changes_made": [],
            "metadata": {"model": "mt5-small", "service": "ai-llm-service"}
        }

    model, tokenizer, device = get_model()

    system_prompt = _load_prompt("ocr_fix")
    input_text = f"{system_prompt}\n\nLanguage: {language}\n\nText: {raw_text}\n\nCorrected:"

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=256,
            num_beams=4,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )

    corrected_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {
        "corrected_text": corrected_text,
        "confidence": 0.85,
        "language": language,
        "changes_made": [],
        "metadata": {"model": "mt5-small", "service": "ai-llm-service"}
    }

