"""
Medical Safety Constraints
Responsibility: Enforce medical safety rules across all LLM outputs
"""

# Forbidden actions
FORBIDDEN_ACTIONS = [
    "diagnose", "prescribe", "recommend treatment",
    "suggest medication", "medical advice"
]

# Required disclaimers
MEDICAL_DISCLAIMER = """
Note: This is informational only. Always consult healthcare professionals 
for medical decisions.
"""

def validate_medical_safety(text: str) -> tuple[bool, list]:
    """
    Validate text does not contain medical advice
    
    Args:
        text: LLM generated text
        
    Returns:
        (is_safe, list_of_violations)
    """
    violations = []
    
    # TODO: Check for diagnosis attempts
    # TODO: Check for prescription recommendations
    # TODO: Check for medical advice language
    # TODO: Flag potential violations
    
    # is_safe = len(violations) == 0
    # return is_safe, violations
    pass


def add_disclaimer(text: str, context: str = "general") -> str:
    """
    Add appropriate medical disclaimer to output
    
    Args:
        text: Generated text
        context: Context type (prescription, chat, etc.)
        
    Returns:
        Text with disclaimer
    """
    # TODO: Add context-appropriate disclaimer
    # TODO: Return text with disclaimer
    pass


def filter_harmful_content(text: str) -> str:
    """
    Remove or flag potentially harmful content
    
    Args:
        text: Generated text
        
    Returns:
        Filtered text or error message
    """
    # TODO: Detect harmful content
    # TODO: Remove or replace with warning
    # TODO: Return safe text
    pass
