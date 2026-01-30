"""
Pydantic schemas for AI LLM Service
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class PatientInfo(BaseModel):
    """Patient information from prescription"""
    name: str = Field(..., description="Patient name")
    id: str = Field(..., description="Patient ID")
    age: Optional[int] = Field(default=None, description="Patient age")
    gender: str = Field(..., description="Patient gender")
    hospital_code: str = Field(..., description="Hospital/clinic code")

class MedicalInfo(BaseModel):
    """Medical information from prescription"""
    diagnosis: str = Field(..., description="Medical diagnosis")
    doctor: str = Field(..., description="Doctor name")
    date: str = Field(..., description="Prescription date")
    department: str = Field(..., description="Hospital department")

class MedicationInfo(BaseModel):
    """Medication information with dosage"""
    name: str = Field(..., description="Medication name")
    dosage: str = Field(default="", description="Dosage information")
    times: List[str] = Field(..., description="Time periods: morning, noon, evening, night")
    times_24h: List[str] = Field(..., description="24-hour format times: 08:00, 12:00, 18:00, 21:00")
    repeat: str = Field(default="daily", description="Repeat frequency")
    duration_days: Optional[int] = Field(default=None, description="Duration in days")
    notes: str = Field(default="", description="Additional notes")

class ComprehensivePrescription(BaseModel):
    """Complete prescription data for medical history"""
    patient_info: PatientInfo = Field(..., description="Patient information")
    medical_info: MedicalInfo = Field(..., description="Medical information")
    medications: List[MedicationInfo] = Field(..., description="Medication list")

class ReminderRequest(BaseModel):
    """Request for structured reminder extraction"""
    raw_ocr_json: Dict[str, Any] = Field(..., description="Raw OCR data as JSON")

class ReminderResponse(BaseModel):
    """Structured reminder response"""
    medications: List[MedicationInfo] = Field(..., description="List of medication reminders")
    success: bool = Field(..., description="Processing success")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class OCRCorrectionRequest(BaseModel):
    """Request for OCR text correction"""
    raw_text: str = Field(..., description="Raw OCR text to correct")
    language: str = Field(default="en", description="Language code: en, km, fr")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class OCRCorrectionResponse(BaseModel):
    """Response after OCR correction"""
    corrected_text: str = Field(..., description="AI-corrected text")
    confidence: float = Field(..., description="Confidence score 0-1")
    changes_made: Optional[List[Dict[str, str]]] = Field(default=None, description="List of corrections")
    language: str = Field(..., description="Detected/confirmed language")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class ChatRequest(BaseModel):
    """Request for chatbot interaction"""
    message: str = Field(..., description="User message")
    language: str = Field(default="en", description="Language code: en, km, fr")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")

class ChatResponse(BaseModel):
    """Response from chatbot"""
    response: str = Field(..., description="Assistant response")
    language: str = Field(..., description="Response language")
    confidence: float = Field(..., description="Response confidence 0-1")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
