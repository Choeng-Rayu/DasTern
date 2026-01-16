"""
Pydantic schemas for AI LLM Service
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

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
