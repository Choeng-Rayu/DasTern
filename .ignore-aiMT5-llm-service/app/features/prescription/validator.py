"""
Prescription Validator
Responsibility: Safety & validation for prescription enhancement
"""

# Medical safety constraints
FORBIDDEN_TERMS = [
    "diagnose", "diagnosis", "cure", "treatment plan",
    "recommend", "prescribe", "you should take"
]

def validate_output(text: str) -> tuple[bool, list]:
    """
    Validate LLM output for medical safety
    
    Args:
        text: LLM generated text
        
    Returns:
        (is_valid, list_of_violations)
    """
    violations = []
    
    # TODO: Check for forbidden medical advice
    # for term in FORBIDDEN_TERMS:
    #     if term in text.lower():
    #         violations.append(f"Contains forbidden term: {term}")
    
    # TODO: Check for hallucinated information
    # TODO: Verify output matches OCR input
    
    # is_valid = len(violations) == 0
    # return is_valid, violations
    pass


def validate_prescription_structure(data: dict) -> bool:
    """
    Validate prescription data structure
    
    Args:
        data: Enhanced prescription data
        
    Returns:
        True if structure is valid
    """
    # TODO: Check required fields
    required = ["medicines", "patient_info"]
    
    # TODO: Validate data types
    # TODO: Check for completeness
    # TODO: Return validation result
    pass


def check_drug_interactions(drug_list: list):
    """
    Basic drug interaction checks (rule-based only)
    
    Args:
        drug_list: List of drugs in prescription
        
    Returns:
        List of potential interactions to flag
    """
    # TODO: Implement basic interaction rules
    # TODO: Flag known dangerous combinations
    # TODO: Return warnings (NOT advice)
    pass
