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


class ParsePrescriptionRequest(BaseModel):
    """Request to parse raw OCR text into structured prescription"""
    raw_text: str
    language: Optional[str] = "en"


class DosageSchedule(BaseModel):
    """Dosage schedule for a medication"""
    morning: int = 0
    noon: int = 0
    evening: int = 0
    night: int = 0


class MedicationData(BaseModel):
    """Structured medication data"""
    name: str
    strength: Optional[str] = None
    form: str = "tablet"
    schedule: DosageSchedule
    total_quantity: Optional[int] = None
    duration_days: Optional[int] = None
    notes: Optional[str] = None


class PatientData(BaseModel):
    """Patient information"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_id: Optional[str] = None


class VitalsData(BaseModel):
    """Vital signs"""
    bp: Optional[str] = None
    pulse: Optional[int] = None
    temperature: Optional[float] = None


class DoctorData(BaseModel):
    """Doctor information"""
    name: Optional[str] = None


class StructuredPrescription(BaseModel):
    """Complete structured prescription"""
    prescription_id: Optional[str] = None
    date: Optional[str] = None
    hospital: Optional[str] = None
    patient: PatientData
    diagnosis_text: Optional[str] = None
    medications: list[MedicationData]
    vitals: Optional[VitalsData] = None
    doctor: DoctorData


class ReminderData(BaseModel):
    """Reminder for a single medication dose"""
    medication_name: str
    strength: Optional[str] = None
    time: str
    time_slot: str
    dose: int
    message_en: str
    message_kh: str


class ParsePrescriptionResponse(BaseModel):
    """Response with parsed prescription data"""
    success: bool
    ai_parsed: bool
    prescription: Optional[StructuredPrescription] = None
    reminders: list[ReminderData] = []
    error: Optional[str] = None


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


# Prompt for parsing prescription from raw OCR text
PARSE_PRESCRIPTION_PROMPT = """You are a medical prescription parser. Parse the following OCR text from a Cambodian prescription image and extract structured data.

The prescription format typically has:
- Header with hospital name, prescription ID, date
- Patient information (name, age, gender, medical ID)
- Diagnosis (store as text only, do NOT interpret)
- Medication table with columns: Medicine Name, Quantity, Morning dose, Noon dose, Evening dose, Night dose
- Vitals (BP, pulse, temperature) if present
- Doctor signature/name

OCR TEXT:
{raw_text}

Extract and return a JSON object with this EXACT structure:
{{
    "prescription_id": "extracted ID or null",
    "date": "YYYY-MM-DD format or null",
    "hospital": "hospital name or null",
    "patient": {{
        "name": "patient name or null",
        "age": number or null,
        "gender": "M/F or null",
        "medical_id": "ID or null"
    }},
    "diagnosis_text": "diagnosis as text only or null",
    "medications": [
        {{
            "name": "medication name (correct spelling)",
            "strength": "dosage like 500mg or null",
            "form": "tablet/capsule/amp/etc",
            "schedule": {{
                "morning": number (0 if not taken),
                "noon": number (0 if not taken),
                "evening": number (0 if not taken),
                "night": number (0 if not taken)
            }},
            "total_quantity": number or null,
            "duration_days": number or null,
            "notes": "special instructions or null"
        }}
    ],
    "vitals": {{
        "bp": "systolic/diastolic or null",
        "pulse": number or null,
        "temperature": number or null
    }} or null,
    "doctor": {{
        "name": "doctor name or null"
    }}
}}

IMPORTANT RULES:
1. Correct common OCR spelling errors in medication names (e.g., "Amxicillin" -> "Amoxicillin")
2. The schedule numbers represent doses, not times. "1 - 1 -" means 1 in morning, 0 at noon, 1 in evening, 0 at night
3. If a dash (-) appears in schedule, it means 0 (no dose at that time)
4. Parse Khmer, English, and French text
5. Store diagnosis as TEXT ONLY - never interpret or suggest treatments
6. Return valid JSON only, no explanations"""


@app.post("/parse-prescription", response_model=ParsePrescriptionResponse)
async def parse_prescription_endpoint(request: ParsePrescriptionRequest):
    """
    Parse raw OCR text into structured prescription data.

    This endpoint uses AI to:
    - Extract prescription metadata (hospital, ID, date, doctor)
    - Extract patient information
    - Parse medication table with dosage schedules
    - Correct OCR spelling errors in medication names
    - Generate reminders based on schedule

    Args:
        request: Raw OCR text and optional language

    Returns:
        Structured prescription data with reminders
    """
    from .core.generation import generate_json

    try:
        raw_text = request.raw_text
        if not raw_text or not raw_text.strip():
            return ParsePrescriptionResponse(
                success=False,
                ai_parsed=False,
                error="No OCR text provided"
            )

        logger.info(f"Parsing prescription from {len(raw_text)} chars of OCR text")

        # Use AI to parse the prescription
        prompt = PARSE_PRESCRIPTION_PROMPT.format(raw_text=raw_text)

        result = generate_json(
            prompt=prompt,
            system_prompt="You are a medical prescription parser. Respond with valid JSON only.",
            temperature=0.1,
            timeout=60
        )

        if not result:
            logger.warning("AI parsing returned no result")
            return ParsePrescriptionResponse(
                success=True,
                ai_parsed=False,
                error="AI could not parse the prescription"
            )

        # Build structured prescription from AI result
        patient_data = result.get("patient", {})
        vitals_data = result.get("vitals")
        doctor_data = result.get("doctor", {})

        medications = []
        for med in result.get("medications", []):
            schedule = med.get("schedule", {})
            medications.append(MedicationData(
                name=med.get("name", "Unknown"),
                strength=med.get("strength"),
                form=med.get("form", "tablet"),
                schedule=DosageSchedule(
                    morning=int(schedule.get("morning", 0) or 0),
                    noon=int(schedule.get("noon", 0) or 0),
                    evening=int(schedule.get("evening", 0) or 0),
                    night=int(schedule.get("night", 0) or 0)
                ),
                total_quantity=med.get("total_quantity"),
                duration_days=med.get("duration_days"),
                notes=med.get("notes")
            ))

        prescription = StructuredPrescription(
            prescription_id=result.get("prescription_id"),
            date=result.get("date"),
            hospital=result.get("hospital"),
            patient=PatientData(
                name=patient_data.get("name"),
                age=patient_data.get("age"),
                gender=patient_data.get("gender"),
                medical_id=patient_data.get("medical_id")
            ),
            diagnosis_text=result.get("diagnosis_text"),
            medications=medications,
            vitals=VitalsData(
                bp=vitals_data.get("bp"),
                pulse=vitals_data.get("pulse"),
                temperature=vitals_data.get("temperature")
            ) if vitals_data else None,
            doctor=DoctorData(name=doctor_data.get("name"))
        )

        # Generate reminders from medication schedules
        reminders = generate_reminders_from_meds(medications)

        logger.info(f"Parsed prescription with {len(medications)} medications, {len(reminders)} reminders")

        return ParsePrescriptionResponse(
            success=True,
            ai_parsed=True,
            prescription=prescription,
            reminders=reminders
        )

    except Exception as e:
        logger.error(f"Prescription parsing failed: {e}")
        return ParsePrescriptionResponse(
            success=False,
            ai_parsed=False,
            error=str(e)
        )


def generate_reminders_from_meds(medications: list[MedicationData]) -> list[ReminderData]:
    """Generate reminder list from medication schedules."""
    reminders = []

    time_slots = {
        "morning": {"time": "07:00", "kh": "ព្រឹក"},
        "noon": {"time": "11:30", "kh": "ថ្ងៃ"},
        "evening": {"time": "17:30", "kh": "ល្ងាច"},
        "night": {"time": "21:00", "kh": "យប់"},
    }

    for med in medications:
        schedule = med.schedule
        strength_text = f" {med.strength}" if med.strength else ""

        for slot_name, slot_config in time_slots.items():
            dose = getattr(schedule, slot_name, 0)
            if dose and dose > 0:
                reminders.append(ReminderData(
                    medication_name=med.name,
                    strength=med.strength,
                    time=slot_config["time"],
                    time_slot=slot_name,
                    dose=dose,
                    message_en=f"Take {dose} {med.form}{'s' if dose > 1 else ''} of {med.name}{strength_text}",
                    message_kh=f"សូមទទួលថ្នាំ {med.name}{strength_text} ចំនួន {dose} គ្រាប់ ពេល{slot_config['kh']}"
                ))

    # Sort by time
    reminders.sort(key=lambda r: r.time)

    return reminders
