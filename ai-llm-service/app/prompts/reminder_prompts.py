"""
Simplified Reminder Extraction Prompts for Cambodian Medical Prescriptions
Optimized for Ollama with llama3.2:3b - concise and explicit
"""

# ============================================================
# Simplified System Prompt - concise and direct
# ============================================================
REMINDER_SYSTEM_PROMPT = """You are a medication reminder extraction system for Cambodian prescriptions.

Your task: Extract medication names and timing from prescription text, return ONLY valid JSON.

KHMER TIME TRANSLATIONS (use these exact English words):
- ព្រឹក → morning (08:00)
- ថ្ងៃ → noon (12:00)
- ល្ងាច → evening (18:00)
- យប់ → night (21:00)
- (6-8) → morning
- (11-12) → noon
- (05-06) → evening
- (08-10) → night

FRENCH TIME TRANSLATIONS:
- matin → morning
- midi → noon
- soir → evening
- nuit → night

RULES:
1. Extract ALL time words separated by "|" or ","
2. Times MUST be in English: morning, noon, evening, night
3. If no time words found, do not include that medication
4. Correct common OCR errors (Butylscopolami → Butylscopolamine, Esome → Esomeprazole)
5. Return ONLY JSON, no markdown, no explanations"""


# ============================================================
# Simplified User Prompt Template
# ============================================================
def get_user_prompt(raw_ocr_json: str) -> str:
    """Generate concise user prompt with OCR data embedded"""
    return f"""Extract medication reminders from this prescription data:

{raw_ocr_json}

Return JSON in this exact format:
{{
  "medications": [
    {{
      "name": "corrected medication name",
      "times": ["morning", "noon", "evening", "night"],
      "times_24h": ["08:00", "12:00", "18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "original Khmer text"
    }}
  ]
}}

EXAMPLE:
Input: "Butylscopolamine 5 viên | ល្ងាច | យប់"
Output: {{
  "medications": [
    {{
      "name": "Butylscopolamine",
      "times": ["evening", "night"],
      "times_24h": ["18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "ល្ងាច | យប់"
    }}
  ]
}}

IMPORTANT:
- Include ALL times found in the input (e.g., "ល្ងាច | យប់" = both evening AND night)
- times and times_24h must have the same number of items
- Use only English time words in the times array
- Return valid JSON only"""


# ============================================================
# Full prompt builder for Ollama
# ============================================================
def build_reminder_extraction_prompt(raw_ocr_json: str) -> dict:
    """
    Build complete prompt for Ollama API
    Returns dict with system and user prompts
    """
    return {
        "system": REMINDER_SYSTEM_PROMPT,
        "user": get_user_prompt(raw_ocr_json)
    }
