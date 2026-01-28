"""
Confidence utilities for AI LLM service
"""
from typing import Optional


def estimate_confidence(text: str) -> float:
    """
    Lightweight heuristic confidence estimate.
    This is a placeholder until a proper scoring model is added.
    """
    if not text or not text.strip():
        return 0.0

    length = len(text.strip())
    if length < 10:
        return 0.4
    if length < 50:
        return 0.7
    return 0.85
