"""
Prompt templates for AI service
"""
from .reminder_prompts import (
    REMINDER_SYSTEM_PROMPT,
    get_user_prompt,
    build_reminder_extraction_prompt
)

__all__ = [
    "REMINDER_SYSTEM_PROMPT",
    "get_user_prompt",
    "build_reminder_extraction_prompt"
]
