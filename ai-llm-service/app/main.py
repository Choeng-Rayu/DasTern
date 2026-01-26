"""
AI LLM Service API Entry Point
FastAPI application for prescription enhancement using LLaMA/Ollama
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .core.model_loader import load_model, is_model_ready, get_model_info
from .features.prescription.enhancer import enhance_prescription
from .features.prescription.validator import validate_prescription
from .safety.medical import (
    is_diagnosis_request, 
    is_drug_advice_request,
    get_safe_refusal
)
from .safety.language import detect_language

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DasTern AI LLM Service",
    description="Prescription enhancement and medical AI using LLaMA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Request/Response Models
class EnhanceRequest(BaseModel):
    """Request for prescription enhancement"""
    ocr_data: Dict[str, Any]
    language: Optional[str] = None


class EnhanceResponse(BaseModel):
    """Response with enhanced prescription"""
    success: bool
    ai_enhanced: bool
    data: Dict[str, Any]
    prescription_summary: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None


class ValidateRequest(BaseModel):
    """Request for prescription validation"""
    prescription_data: Dict[str, Any]


class ChatRequest(BaseModel):
    """Request for chatbot interaction"""
    message: str
    prescription_context: Optional[Dict[str, Any]] = None
    language: Optional[str] = None


class ChatResponse(BaseModel):
    """Chatbot response"""
    message: str
    is_safe_response: bool
    detected_language: str


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    logger.info("Initializing AI LLM Service...")
    try:
        load_model()
        logger.info("Model initialization complete")
    except Exception as e:
        logger.warning(f"Model not available at startup: {e}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "DasTern AI LLM Service",
        "status": "ready" if is_model_ready() else "model_not_loaded",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    model_info = get_model_info()
    return {
        "status": "healthy" if model_info["is_loaded"] else "degraded",
        "model": model_info,
        "components": {
            "enhancer": "ready",
            "validator": "ready",
            "safety": "ready"
        }
    }


@app.post("/enhance", response_model=EnhanceResponse)
async def enhance_endpoint(request: EnhanceRequest):
    """
    Enhance OCR prescription data with AI descriptions.
    
    Takes raw OCR output and adds:
    - Medication descriptions
    - Dosage instructions in multiple languages
    - Warnings and safety information
    - Prescription summary
    """
    try:
        ocr_data = request.ocr_data
        
        # Enhance prescription
        enhanced = enhance_prescription(ocr_data)
        
        # Validate enhanced data
        validation = validate_prescription(enhanced)
        
        return EnhanceResponse(
            success=True,
            ai_enhanced=enhanced.get("ai_enhanced", False),
            data=enhanced,
            prescription_summary=enhanced.get("prescription_summary"),
            validation=validation
        )
        
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        # Return original data without AI enhancement
        return EnhanceResponse(
            success=True,
            ai_enhanced=False,
            data=request.ocr_data,
            prescription_summary=None,
            validation=None
        )


@app.post("/validate")
async def validate_endpoint(request: ValidateRequest):
    """Validate prescription for safety issues."""
    try:
        validation = validate_prescription(request.prescription_data)
        return validation
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Prescription-aware chatbot endpoint.
    
    Can answer questions about a prescription but will not:
    - Diagnose conditions
    - Recommend medications
    - Provide medical advice
    """
    from .core.generation import generate
    
    message = request.message
    detected_lang = detect_language(message)
    
    # Safety checks
    if is_diagnosis_request(message):
        return ChatResponse(
            message=get_safe_refusal("diagnosis"),
            is_safe_response=True,
            detected_language=detected_lang
        )
    
    if is_drug_advice_request(message):
        return ChatResponse(
            message=get_safe_refusal("drug_advice"),
            is_safe_response=True,
            detected_language=detected_lang
        )
    
    # Build context from prescription if provided
    context = ""
    if request.prescription_context:
        meds = request.prescription_context.get("structured_data", {}).get("medications", [])
        if meds:
            context = "Current prescription medications:\n"
            for med in meds:
                context += f"- {med.get('name', 'Unknown')}: {med.get('strength', '')}\n"
    
    # Generate response
    system_prompt = """You are a helpful pharmacy assistant. You can only:
1. Explain what prescribed medications are used for
2. Clarify dosage instructions from prescriptions
3. Remind about general medication safety

You CANNOT:
- Diagnose any condition
- Recommend medications
- Suggest changing dosages
- Provide medical advice

Always recommend consulting a doctor for medical concerns."""

    try:
        response = generate(
            prompt=f"{context}\n\nUser question: {message}",
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        if response:
            return ChatResponse(
                message=response,
                is_safe_response=True,
                detected_language=detected_lang
            )
        else:
            return ChatResponse(
                message="I apologize, but I'm unable to respond right now. Please try again later.",
                is_safe_response=True,
                detected_language=detected_lang
            )
            
    except Exception as e:
        logger.error(f"Chat generation failed: {e}")
        return ChatResponse(
            message="I'm having trouble responding. Please consult your pharmacist or doctor.",
            is_safe_response=True,
            detected_language=detected_lang
        )
