"""
Prompt templates for AI service
"""
from .reminder_prompts import (
    REMINDER_SYSTEM_PROMPT,
    TIME_NORMALIZATION_TABLE,
    get_user_prompt,
    build_reminder_extraction_prompt,
    FEW_SHOT_EXAMPLES
)

__all__ = [
    "REMINDER_SYSTEM_PROMPT",
    "TIME_NORMALIZATION_TABLE", 
    "get_user_prompt",
    "build_reminder_extraction_prompt",
    "FEW_SHOT_EXAMPLES"
]
