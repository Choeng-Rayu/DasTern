"""
Request schemas for the OCR Service API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class OCRRequest(BaseModel):
    """Request configuration for OCR processing."""
    
    languages: Optional[str] = Field(
        default=None,
        description="Override languages, e.g., 'eng+khm+fra'",
        examples=["eng+khm", "eng+khm+fra"]
    )
    skip_enhancement: bool = Field(
        default=False,
        description="Skip preprocessing if image is already clean"
    )
    include_confidence: bool = Field(
        default=True,
        description="Include confidence scores in output"
    )
    min_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold (0-1)"
    )


class TrainingUploadRequest(BaseModel):
    """Request for uploading training data."""
    
    model_name: str = Field(
        description="Name for the model being trained",
        examples=["khm_prescription_v1"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of training data"
    )


class TrainingAnnotateRequest(BaseModel):
    """Request for annotation generation."""
    
    image_id: str = Field(
        description="ID of uploaded image to annotate"
    )
    corrections: Optional[dict] = Field(
        default=None,
        description="Manual corrections to apply"
    )


class TrainingStartRequest(BaseModel):
    """Request to start model training."""
    
    model_name: str = Field(
        description="Name for the new model"
    )
    base_model: str = Field(
        default="khm",
        description="Base language model to fine-tune"
    )
    epochs: int = Field(
        default=400,
        ge=100,
        le=10000,
        description="Number of training iterations"
    )
    learning_rate: float = Field(
        default=0.001,
        ge=0.0001,
        le=0.1,
        description="Learning rate for training"
    )
