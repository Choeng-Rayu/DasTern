"""
Prescription Enhancer
Uses LLM to enhance and describe OCR output
"""

import logging
from typing import Dict, Any, List, Optional

from ...core.generation import generate_json, generate

logger = logging.getLogger(__name__)

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

