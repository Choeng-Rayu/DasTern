"""
AI OCR Corrector Module using MT5-Small

Uses prefix-based prompting for OCR error correction.
Supports: English, Khmer, French medical prescription text.

Model: google/mt5-small (300M params, CPU-compatible)
Purpose: OCR error correction, NOT OCR itself
"""

import os
from typing import Optional, Dict, Tuple
from functools import lru_cache

# Lazy loading for transformers (heavy imports)
_model = None
_tokenizer = None


def get_model_paths() -> Tuple[str, str]:
    """Get paths for local model files."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tokenizer_path = os.path.join(base_dir, "ai", "mt5", "tokenizer")
    model_path = os.path.join(base_dir, "ai", "mt5", "model")
    return tokenizer_path, model_path


def load_model(use_local: bool = True, device: str = "cpu"):
    """
    Load MT5 model and tokenizer.
    Uses local fine-tuned model if available, else downloads from HuggingFace.
    """
    global _model, _tokenizer
    
    if _model is not None and _tokenizer is not None:
        return _tokenizer, _model
    
    from transformers import MT5ForConditionalGeneration, MT5Tokenizer
    import torch
    
    tokenizer_path, model_path = get_model_paths()
    
    # Try local first
    if use_local and os.path.exists(tokenizer_path) and os.path.exists(model_path):
        print("Loading local fine-tuned MT5 model...")
        _tokenizer = MT5Tokenizer.from_pretrained(tokenizer_path)
        _model = MT5ForConditionalGeneration.from_pretrained(model_path)
    else:
        print("Loading MT5-small from HuggingFace...")
        model_name = "google/mt5-small"
        _tokenizer = MT5Tokenizer.from_pretrained(model_name)
        _model = MT5ForConditionalGeneration.from_pretrained(model_name)
    
    _model.to(device)
    _model.eval()  # Set to evaluation mode
    
    return _tokenizer, _model


def ai_correct(text: str, lang: str = "eng", max_length: int = 128, num_beams: int = 4) -> str:
    """
    Correct OCR errors using MT5 model.
    
    Args:
        text: Raw OCR text with potential errors
        lang: Language code (eng, khm, fra)
        max_length: Maximum output length
        num_beams: Beam search width (higher = better but slower)
        
    Returns:
        Corrected text
    """
    if not text or not text.strip():
        return ""
    
    import torch
    
    tokenizer, model = load_model()
    
    # Prefix-based prompting - critical for MT5 task understanding
    prompt = f"fix_ocr_{lang}: {text}"
    
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True
    )
    
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            num_beams=num_beams,
            early_stopping=True,
            no_repeat_ngram_size=2
        )
    
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return corrected


def ai_correct_batch(texts: list, lang: str = "eng", max_length: int = 128) -> list:
    """
    Batch correction for multiple text blocks.
    More efficient than calling ai_correct multiple times.
    """
    if not texts:
        return []
    
    import torch
    
    tokenizer, model = load_model()
    
    prompts = [f"fix_ocr_{lang}: {t}" for t in texts]
    
    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True
    )
    
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            num_beams=2,  # Reduced for batch efficiency
            early_stopping=True
        )
    
    return [tokenizer.decode(o, skip_special_tokens=True) for o in outputs]


def detect_and_correct(text: str) -> Dict:
    """
    Auto-detect language and apply correction.
    """
    from .ocr_engine import detect_language_hint, Language
    
    lang_hint = detect_language_hint(text)
    
    lang_map = {
        Language.ENGLISH: "eng",
        Language.KHMER: "khm",
        Language.FRENCH: "fra",
        Language.ENGLISH_FRENCH: "eng",
        Language.ALL: "eng"
    }
    
    lang = lang_map.get(lang_hint, "eng")
    corrected = ai_correct(text, lang)
    
    return {
        "original": text,
        "corrected": corrected,
        "detected_language": lang_hint.value
    }


def is_model_available() -> bool:
    """Check if model is loaded and ready."""
    return _model is not None and _tokenizer is not None


def unload_model():
    """Free memory by unloading model."""
    global _model, _tokenizer
    _model = None
    _tokenizer = None
    
    import gc
    import torch
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

