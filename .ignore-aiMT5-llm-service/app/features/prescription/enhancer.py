"""
Prescription Enhancer
Responsibility: Clean and normalize OCR output using LLM
Input: OCR structured JSON
Output: Clean, normalized prescription
"""

# TODO: from core.generation import generate

def enhance_prescription(ocr_json: dict, language: str = "en"):
    """
    Enhance and normalize prescription OCR output
    
    Args:
        ocr_json: Structured OCR result from OCR service
        language: Target language (en, kh, fr)
        
    Returns:
        Enhanced prescription data
    """
    # TODO: Build enhancement prompt
    # prompt = f"""
    # You are a medical prescription processor.
    # Clean and normalize the following OCR data.
    # 
    # OCR Data: {ocr_json}
    # 
    # Rules:
    # - Fix spelling errors
    # - Standardize drug names
    # - Normalize dosage formats
    # - DO NOT add information not in OCR
    # - DO NOT diagnose or give medical advice
    # """
    
    # TODO: Generate enhanced output
    # enhanced = generate(prompt, max_tokens=1024)
    
    # TODO: Parse and validate output
    # TODO: Return structured result
    pass


def normalize_drug_names(drug_list: list):
    """
    Normalize drug names to standard format
    
    Args:
        drug_list: List of drug names from OCR
        
    Returns:
        Normalized drug names
    """
    # TODO: Use LLM to normalize drug names
    # TODO: Handle multiple languages
    # TODO: Return standardized names
    pass


def extract_dosage_info(text: str):
    """
    Extract structured dosage information
    
    Args:
        text: Raw dosage text
        
    Returns:
        Structured dosage (amount, frequency, duration)
    """
    # TODO: Parse dosage patterns
    # TODO: Extract amount, frequency, duration
    # TODO: Return structured data
    pass
