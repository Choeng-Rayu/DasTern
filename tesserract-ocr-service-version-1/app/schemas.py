"""
Structured JSON Output Schemas

Defines output format for OCR pipeline results.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class LanguageCode(str, Enum):
    ENGLISH = "eng"
    KHMER = "khm"
    FRENCH = "fra"


class RegionType(str, Enum):
    HEADER = "header"
    BODY = "body"
    TABLE = "table"
    SIGNATURE = "signature"
    FOOTER = "footer"


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    confidence: float = 1.0


class TextBlock(BaseModel):
    raw_text: str = Field(description="Original OCR output")
    corrected_text: str = Field(description="Rule-based cleaned text (no AI)")
    final_text: str = Field(description="Post-processed clean text")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    region_type: RegionType = RegionType.BODY
    bounding_box: Optional[BoundingBox] = None
    detected_language: Optional[LanguageCode] = None
    needs_review: bool = False


class QualityMetrics(BaseModel):
    blur_score: float
    brightness: float
    contrast: float
    resolution: Dict[str, int]
    passed: bool
    message: str


class OCRResult(BaseModel):
    """Complete OCR pipeline result."""
    success: bool
    languages: List[LanguageCode] = [LanguageCode.ENGLISH, LanguageCode.KHMER, LanguageCode.FRENCH]
    text_blocks: List[TextBlock] = []
    full_text: str = Field(description="Concatenated final text from all blocks")
    medications: List[Medication] = []
    overall_confidence: float = Field(ge=0.0, le=1.0)
    needs_review: bool = False
    quality_metrics: Optional[QualityMetrics] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class OCRRequest(BaseModel):
    """Request schema for OCR endpoint."""
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    languages: List[LanguageCode] = [LanguageCode.ENGLISH, LanguageCode.KHMER, LanguageCode.FRENCH]
    lenient_quality: bool = False


def build_text_block(region: Dict) -> TextBlock:
    """Convert internal region dict to TextBlock schema."""
    box = region.get("box")
    bounding_box = None
    if box:
        bounding_box = BoundingBox(
            x=box[0], y=box[1], width=box[2], height=box[3]
        )
    
    return TextBlock(
        raw_text=region.get("raw", ""),
        corrected_text=region.get("cleaned", region.get("raw", "")),
        final_text=region.get("final", ""),
        confidence=region.get("confidence", 0.5),
        region_type=RegionType(region.get("type", "body")),
        bounding_box=bounding_box,
        detected_language=region.get("detected_language"),
        needs_review=region.get("needs_review", False)
    )


def build_output(regions: List[Dict], quality_metrics: Dict = None, 
                 processing_time: int = None, error: str = None) -> Dict:
    """
    Build structured output from pipeline results.
    
    Args:
        regions: List of processed region dictionaries
        quality_metrics: Image quality check results
        processing_time: Processing time in milliseconds
        error: Error message if any
        
    Returns:
        Dictionary matching OCRResult schema
    """
    if error:
        return {
            "success": False,
            "languages": ["eng", "khm", "fra"],
            "text_blocks": [],
            "full_text": "",
            "medications": [],
            "overall_confidence": 0.0,
            "needs_review": True,
            "quality_metrics": quality_metrics,
            "processing_time_ms": processing_time,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    text_blocks = []
    all_medications = []
    confidences = []
    full_text_parts = []
    
    for region in regions:
        text_blocks.append({
            "raw_text": region.get("raw", ""),
            "corrected_text": region.get("cleaned", region.get("raw", "")),
            "final_text": region.get("final", ""),
            "confidence": region.get("confidence", 0.5),
            "region_type": region.get("type", "body"),
            "bounding_box": {
                "x": region["box"][0],
                "y": region["box"][1],
                "width": region["box"][2],
                "height": region["box"][3]
            } if region.get("box") else None,
            "detected_language": region.get("detected_language"),
            "needs_review": region.get("needs_review", False)
        })
        
        confidences.append(region.get("confidence", 0.5))
        full_text_parts.append(region.get("final", ""))
        all_medications.extend(region.get("medications", []))
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    needs_review = avg_confidence < 0.7 or any(r.get("needs_review") for r in regions)
    
    return {
        "success": True,
        "languages": ["eng", "khm", "fra"],
        "text_blocks": text_blocks,
        "full_text": "\n".join(full_text_parts),
        "medications": all_medications,
        "overall_confidence": round(avg_confidence, 2),
        "needs_review": needs_review,
        "quality_metrics": quality_metrics,
        "processing_time_ms": processing_time,
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }

