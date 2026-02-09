"""
<<<<<<< HEAD
Prescription Enhancer
Uses LLM to enhance and describe OCR output
"""

import logging
=======
Prescription Enhancer - Updated for Few-Shot Learning
Uses LLM to enhance and describe OCR output with training examples
"""

import json
import logging
import os
>>>>>>> 479e2f047f47a189e6575eb2c4ec1dee4038fac6
from typing import Dict, Any, List, Optional

from ...core.generation import generate_json, generate

logger = logging.getLogger(__name__)

<<<<<<< HEAD
# System prompt for prescription enhancement
ENHANCER_SYSTEM_PROMPT = """You are a medical prescription analyzer assistant.
Your job is to analyze OCR-extracted prescription data and provide:
1. Cleaned and verified medication information
2. Clear dosage instructions in both English and Khmer
3. Important warnings or notes about the medications
4. A brief description of each medication's purpose

IMPORTANT RULES:
- DO NOT diagnose conditions
- DO NOT recommend alternative medications
- DO NOT provide medical advice beyond what's on the prescription
- Only clarify and describe what's already prescribed
- Be accurate - if uncertain, say so
- Support Khmer, English, and French text

Respond with valid JSON only."""

MEDICATION_DESCRIPTION_PROMPT = """Analyze this medication and provide a brief, patient-friendly description:

Medication: {name}
Strength: {strength}
Dosage Schedule: {schedule}

Provide a JSON response with:
{{
    "name": "verified medication name",
    "description": "1-2 sentence description of what this medication does",
    "category": "medication category (e.g., pain relief, antibiotic, etc.)",
    "common_uses": ["use1", "use2"],
    "warnings": ["any important warnings for this specific medication"],
    "instructions_en": "clear dosage instructions in English",
    "instructions_kh": "clear dosage instructions in Khmer"
}}"""


def enhance_prescription(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance OCR prescription data with AI descriptions.
    
    Args:
        ocr_data: Raw OCR output with medications
        
    Returns:
        Enhanced prescription data with descriptions
    """
    enhanced = ocr_data.copy()
    enhanced["ai_enhanced"] = False
    enhanced["ai_error"] = None
    
    try:
        medications = ocr_data.get("structured_data", {}).get("medications", [])
        
        if not medications:
            logger.info("No medications to enhance")
            return enhanced
        
        enhanced_medications = []
        
        for med in medications:
            enhanced_med = enhance_medication(med)
            enhanced_medications.append(enhanced_med)
        
        # Update structured data with enhanced medications
        if "structured_data" not in enhanced:
            enhanced["structured_data"] = {}
        enhanced["structured_data"]["medications"] = enhanced_medications
        enhanced["ai_enhanced"] = True
        
        # Add overall prescription description
        enhanced["prescription_summary"] = generate_prescription_summary(
            medications=enhanced_medications,
            patient_name=ocr_data.get("structured_data", {}).get("patient_name"),
            date=ocr_data.get("structured_data", {}).get("date")
        )
        
        logger.info(f"Enhanced {len(enhanced_medications)} medications")
        
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        enhanced["ai_error"] = str(e)
    
    return enhanced


def enhance_medication(med: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance a single medication with AI description.
    
    Args:
        med: Medication dict from OCR
        
    Returns:
        Enhanced medication with description
    """
    enhanced = med.copy()
    enhanced["ai_description"] = None
    
    try:
        # Format schedule for prompt
        schedule = med.get("dosage_schedule", {})
        schedule_str = ", ".join(f"{k}: {v}" for k, v in schedule.items()) if schedule else "Not specified"
        
        prompt = MEDICATION_DESCRIPTION_PROMPT.format(
            name=med.get("name", "Unknown"),
            strength=med.get("strength", "Not specified"),
            schedule=schedule_str
        )
        
        result = generate_json(
            prompt=prompt,
            system_prompt=ENHANCER_SYSTEM_PROMPT,
            temperature=0.2
        )
        
        if result:
            enhanced["ai_description"] = result.get("description")
            enhanced["category"] = result.get("category")
            enhanced["common_uses"] = result.get("common_uses", [])
            enhanced["warnings"] = result.get("warnings", [])
            enhanced["instructions_en"] = result.get("instructions_en")
            enhanced["instructions_kh"] = result.get("instructions_kh")
            
            # Verify/correct name if AI suggests different
            if result.get("name") and result["name"].lower() != med.get("name", "").lower():
                enhanced["verified_name"] = result["name"]
                
    except Exception as e:
        logger.warning(f"Failed to enhance medication {med.get('name')}: {e}")
    
    return enhanced


def generate_prescription_summary(
    medications: List[Dict], 
    patient_name: str = None,
    date: str = None
) -> Optional[str]:
    """Generate overall prescription summary."""
    try:
        med_list = "\n".join([
            f"- {m.get('name', 'Unknown')}: {m.get('ai_description', 'No description')}"
            for m in medications
        ])
        
        prompt = f"""Summarize this prescription in 2-3 sentences for a patient:
Patient: {patient_name or 'Not specified'}
Date: {date or 'Not specified'}
Medications:
{med_list}

Provide a simple, patient-friendly summary of what this prescription contains."""
        
        return generate(
            prompt=prompt,
            system_prompt="You are a helpful pharmacy assistant. Be brief and clear.",
            temperature=0.3
        )
    except Exception as e:
        logger.warning(f"Failed to generate summary: {e}")
        return None
=======
class PrescriptionEnhancer:
    def __init__(self):
        self.system_prompt = self._load_system_prompt()
        self.few_shot_examples = self._load_few_shot_examples()
        
    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts module"""
        try:
            from prompts.medical_system_prompt import MEDICAL_EXTRACTION_SYSTEM_PROMPT
            return MEDICAL_EXTRACTION_SYSTEM_PROMPT
        except ImportError:
            logger.warning("Could not import system prompt, using fallback")
            return "You are a medical prescription data extraction expert. Extract structured JSON data from prescription text."
    
    def _load_few_shot_examples(self) -> List[Dict]:
        """Load few-shot examples from training data"""
        try:
            examples = []
            file_path = os.path.join(os.path.dirname(__file__), '../../../data/training/sample_prescriptions.jsonl')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            examples.append(json.loads(line))
                            
            logger.info(f"Loaded {len(examples)} few-shot examples")
            return examples
            
        except Exception as e:
            logger.warning(f"Could not load few-shot examples: {e}")
            return []
    
    def _build_few_shot_prompt(self, raw_ocr_text: str) -> str:
        """Build complete prompt with system instructions and few-shot examples"""
        
        prompt_parts = [self.system_prompt, "\n\nFEW-SHOT LEARNING EXAMPLES:\n"]
        
        # Add 2 best examples
        for i, example in enumerate(self.few_shot_examples[:2], 1):
            prompt_parts.extend([
                f"EXAMPLE {i}:",
                f"INPUT: {example['user']}",
                f"OUTPUT: {example['assistant']}",
                "\n" + "="*80 + "\n"
            ])
        
        # Add current task
        prompt_parts.extend([
            "Now extract structured data from this prescription:",
            f"INPUT: {raw_ocr_text}",
            "OUTPUT:"
        ])
        
        return "\n".join(prompt_parts)
    
    def parse_prescription(self, raw_text: str) -> Optional[Dict]:
        """
        Main parsing function - converts raw OCR text to structured JSON
        
        Args:
            raw_text: Raw, unstructured OCR output from medical prescription
            
        Returns:
            Structured prescription data dictionary or None if parsing fails
        """
        try:
            logger.info(f"Parsing prescription text ({len(raw_text)} characters)")
            
            # Build few-shot prompt
            complete_prompt = self._build_few_shot_prompt(raw_text)
            
            # Call your existing generation.py with optimized parameters
            response = generate(
                prompt=complete_prompt,
                temperature=0.1,  # Low temperature for consistent, accurate extraction
                max_tokens=2000,   # Enough for complex prescriptions
                system_prompt="You are a precise medical data extraction AI. Output valid JSON only."
            )
            
            if not response:
                logger.error("No response received from LLaMA")
                return None
            
            response_text = response.strip()
            logger.debug(f"LLaMA response: {response_text[:200]}...")
            
            # Parse JSON response
            try:
                parsed_data = json.loads(response_text)
                logger.info("✅ Successfully parsed prescription data")
                return parsed_data
                
            except json.JSONDecodeError:
                # Try to extract JSON from mixed response
                logger.warning("JSON parsing failed, attempting to extract JSON block")
                
                # Find JSON block in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_block = response_text[start_idx:end_idx]
                    parsed_data = json.loads(json_block)
                    logger.info("✅ Successfully extracted JSON from mixed response")
                    return parsed_data
                else:
                    logger.error("Could not find valid JSON in response")
                    return None
                    
        except Exception as e:
            logger.error(f"Prescription parsing failed: {e}")
            return None

    def enhance_prescription(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main API function for /enhance endpoint
        Integrates with existing validator.py for safety
        
        Args:
            ocr_data: OCR service output (various formats supported)
            
        Returns:
            Enhanced prescription with AI improvements and validation
        """
        try:
            # Extract raw text from OCR data (handle various formats)
            raw_text = self._extract_raw_text_from_ocr(ocr_data)
            
            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    "success": False,
                    "error": "No usable text found in OCR data",
                    "debug_info": {"ocr_keys": list(ocr_data.keys()) if isinstance(ocr_data, dict) else "not_dict"}
                }
            
            logger.info(f"Processing OCR text: {len(raw_text)} chars")
            
            # Extract structured data using few-shot learning
            extracted_data = self.parse_prescription(raw_text)
            
            if not extracted_data:
                return {
                    "success": False,
                    "error": "Failed to extract structured data from prescription",
                    "raw_text": raw_text
                }
            
            # Validate using your existing validator.py
            validation_result = self._validate_extracted_data(extracted_data)
            
            # Build enhanced response
            enhanced_result = {
                "success": True,
                "ai_enhanced": True,
                "extraction_method": "few_shot_learning_llama3.2",
                "raw_ocr_text": raw_text,
                "extracted_data": extracted_data,
                "validation": validation_result,
                "metadata": {
                    "model_used": "llama3.2:3b",
                    "num_examples_used": len(self.few_shot_examples),
                    "confidence": extracted_data.get("confidence_score", 0.0),
                    "language": extracted_data.get("language_detected", "unknown"),
                    "processing_timestamp": self._get_timestamp()
                }
            }
            
            logger.info(f"✅ Successfully enhanced prescription (confidence: {extracted_data.get('confidence_score', 0):.2f})")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Prescription enhancement failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Enhancement failed: {str(e)}",
                "raw_text": raw_text if 'raw_text' in locals() else None
            }
    
    def _extract_raw_text_from_ocr(self, ocr_data: Dict) -> str:
        """Extract raw text from various OCR output formats"""
        
        if isinstance(ocr_data, str):
            return ocr_data
            
        # Try common OCR output keys
        for key in ["raw_text", "text", "content", "ocr_text"]:
            if key in ocr_data and ocr_data[key]:
                return str(ocr_data[key])
        
        # Handle nested structures
        if "ocr_data" in ocr_data:
            return self._extract_raw_text_from_ocr(ocr_data["ocr_data"])
        
        if "structured_data" in ocr_data:
            # Flatten structured OCR data into text
            structured = ocr_data["structured_data"]
            text_parts = []
            
            if isinstance(structured, dict):
                for key, value in structured.items():
                    if value:
                        text_parts.append(f"{key}: {value}")
            
            return "\n".join(text_parts)
        
        # Last resort - convert entire object to string
        return str(ocr_data)
    
    def _validate_extracted_data(self, extracted_data: Dict) -> Dict:
        """Validate extracted data using existing validator.py"""
        try:
            from ...validator import validate_prescription
            return validate_prescription(extracted_data)
        except ImportError:
            logger.warning("Validator not available, skipping validation")
            return {"warnings": [], "errors": [], "safe": True}
        except Exception as e:
            logger.warning(f"Validation failed: {e}")
            return {"warnings": [f"Validation error: {e}"], "errors": [], "safe": False}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Global enhancer instance for API use
prescription_enhancer = PrescriptionEnhancer()

# Import fast parser for quick extraction
try:
    from .fast_parser import FastPrescriptionParser
    fast_parser = FastPrescriptionParser()
    FAST_PARSER_AVAILABLE = True
except ImportError:
    fast_parser = None
    FAST_PARSER_AVAILABLE = False

def enhance_prescription(ocr_data: Dict[str, Any], use_fast_mode: bool = True) -> Dict[str, Any]:
    """
    Main function called by your existing API endpoint
    This maintains compatibility with your current main.py
    
    Args:
        ocr_data: OCR output data
        use_fast_mode: If True, use fast rule-based parser (default)
                       If False, use LLM-based extraction (slower but potentially more accurate)
    """
    # Extract raw text first
    if isinstance(ocr_data, str):
        raw_text = ocr_data
    else:
        raw_text = prescription_enhancer._extract_raw_text_from_ocr(ocr_data)
    
    # Use fast parser as primary method for speed
    if use_fast_mode and FAST_PARSER_AVAILABLE and fast_parser:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Using fast rule-based parser for quick extraction")
        
        try:
            extracted_data = fast_parser.parse(raw_text)
            
            # Validate the extraction
            validation = prescription_enhancer._validate_extracted_data(extracted_data)
            
            return {
                "success": True,
                "ai_enhanced": False,  # Fast mode doesn't use AI
                "extraction_method": "fast_rule_based",
                "raw_ocr_text": raw_text,
                "extracted_data": extracted_data,
                "validation": validation,
                "metadata": {
                    "model_used": "rule_based_v1",
                    "confidence": extracted_data.get("confidence_score", 0.5),
                    "language": extracted_data.get("language_detected", "unknown"),
                    "processing_timestamp": prescription_enhancer._get_timestamp()
                }
            }
        except Exception as e:
            logger.warning(f"Fast parser failed: {e}, falling back to LLM")
    
    # Fallback to LLM-based extraction
    return prescription_enhancer.enhance_prescription(ocr_data)

def parse_prescription(raw_text: str) -> Optional[Dict]:
    """
    Direct parsing function for raw text input
    Useful for testing and development
    """
    # Use fast parser if available
    if FAST_PARSER_AVAILABLE and fast_parser:
        return fast_parser.parse(raw_text)
    return prescription_enhancer.parse_prescription(raw_text)
>>>>>>> 479e2f047f47a189e6575eb2c4ec1dee4038fac6

