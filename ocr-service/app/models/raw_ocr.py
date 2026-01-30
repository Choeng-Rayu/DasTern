"""
Raw OCR Models
Pydantic models for raw OCR output
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .bbox import BBox


class OCRElement(BaseModel):
    """Single OCR detected element"""
    text: str = Field(..., description="Detected text")
    confidence: int = Field(..., description="Confidence score (0-100, -1 for non-text)")
    bbox: BBox = Field(..., description="Bounding box")
    block: int = Field(..., description="Block number")
    paragraph: int = Field(default=0, description="Paragraph number")
    line: int = Field(..., description="Line number within block")
    word: int = Field(..., description="Word number within line")


class OCRPageResult(BaseModel):
    """OCR result for a single page"""
    page: int = Field(default=1, description="Page number")
    raw: List[OCRElement] = Field(default_factory=list, description="Raw OCR elements")
    stats: Optional[Dict[str, Any]] = Field(default=None, description="Page statistics")


class OCRRequest(BaseModel):
    """Request model for OCR processing"""
    apply_preprocessing: bool = Field(default=True, description="Apply image preprocessing")
    languages: Optional[str] = Field(default=None, description="OCR languages (e.g., 'khm+eng+fra')")
    include_low_confidence: bool = Field(default=True, description="Include low confidence results")


class OCRResponse(BaseModel):
    """Response model for OCR API"""
    success: bool = Field(..., description="Whether OCR was successful")
    page: int = Field(default=1, description="Page number")
    raw: List[Dict[str, Any]] = Field(default_factory=list, description="Raw OCR results")
    stats: Optional[Dict[str, Any]] = Field(default=None, description="OCR statistics")
    languages_used: str = Field(default="khm+eng+fra", description="Languages used for OCR")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    tesseract_installed: bool = Field(..., description="Tesseract availability")
    available_languages: List[str] = Field(default_factory=list, description="Available OCR languages")
    version: str = Field(..., description="Service version")
