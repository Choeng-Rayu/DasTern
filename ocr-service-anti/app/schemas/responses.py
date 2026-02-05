"""
Response schemas for the OCR Service API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class BlurLevel(str, Enum):
    """Blur level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ContrastLevel(str, Enum):
    """Contrast level classification."""
    LOW = "low"
    OK = "ok"
    HIGH = "high"


class BlockType(str, Enum):
    """Type of detected block."""
    HEADER = "header"
    TABLE = "table"
    TEXT = "text"
    FOOTER = "footer"
    SIGNATURE = "signature"
    QR_CODE = "qr_code"
    VITAL_SIGNS = "vital_signs"
    UNKNOWN = "unknown"


class BoundingBox(BaseModel):
    """Bounding box coordinates [x, y, width, height]."""
    x: int = Field(description="X coordinate (left)")
    y: int = Field(description="Y coordinate (top)")
    width: int = Field(description="Width in pixels")
    height: int = Field(description="Height in pixels")
    
    def to_list(self) -> List[int]:
        return [self.x, self.y, self.width, self.height]


class TextLine(BaseModel):
    """A single line of recognized text."""
    
    text: str = Field(description="Recognized text content")
    bbox: BoundingBox = Field(description="Bounding box for this line")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="OCR confidence score (0-1)"
    )
    language: Optional[str] = Field(
        default=None,
        description="Detected language code"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Semantic tags (e.g., 'time_candidate', 'medicine_name')"
    )


class TableCell(BaseModel):
    """A cell within a detected table."""
    
    row: int = Field(description="Row index (0-based)")
    col: int = Field(description="Column index (0-based)")
    text: str = Field(description="Cell text content")
    bbox: BoundingBox = Field(description="Cell bounding box")
    confidence: float = Field(ge=0.0, le=1.0)


class TableBlock(BaseModel):
    """A detected table structure."""
    
    rows: int = Field(description="Number of rows")
    cols: int = Field(description="Number of columns")
    headers: List[str] = Field(
        default_factory=list,
        description="Column header texts"
    )
    cells: List[TableCell] = Field(
        default_factory=list,
        description="Table cells"
    )


class Block(BaseModel):
    """A detected layout block (text region, table, etc.)."""
    
    type: BlockType = Field(description="Type of block")
    bbox: BoundingBox = Field(description="Block bounding box")
    lines: List[TextLine] = Field(
        default_factory=list,
        description="Text lines within this block"
    )
    table: Optional[TableBlock] = Field(
        default=None,
        description="Table structure if type is TABLE"
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="Concatenated text content"
    )


class QRCodeData(BaseModel):
    """Decoded QR code information."""
    
    data: str = Field(description="Decoded QR content")
    bbox: BoundingBox = Field(description="QR code bounding box")
    type: str = Field(default="QR", description="Barcode type")


class QualityMetrics(BaseModel):
    """Image quality analysis results."""
    
    blur: BlurLevel = Field(description="Blur level assessment")
    blur_score: float = Field(description="Raw blur score (Laplacian variance)")
    contrast: ContrastLevel = Field(description="Contrast level assessment")
    contrast_score: float = Field(description="Raw contrast score (std dev)")
    skew_angle: float = Field(description="Detected skew angle in degrees")
    dpi: Optional[int] = Field(default=None, description="Estimated DPI")
    is_grayscale: bool = Field(description="Whether image is grayscale")


class ProcessingMeta(BaseModel):
    """Metadata about the OCR processing."""
    
    languages: List[str] = Field(description="Languages used for OCR")
    dpi: Optional[int] = Field(default=None, description="Image DPI")
    processing_time_ms: float = Field(description="Total processing time in ms")
    model_version: str = Field(default="default", description="OCR model version")
    stage_times: Dict[str, float] = Field(
        default_factory=dict,
        description="Processing time per stage in ms"
    )
    image_size: Dict[str, int] = Field(
        default_factory=dict,
        description="Original image dimensions"
    )


class OCRResponse(BaseModel):
    """Complete OCR response with all extracted data."""
    
    meta: ProcessingMeta = Field(description="Processing metadata")
    quality: QualityMetrics = Field(description="Image quality metrics")
    qr_codes: List[QRCodeData] = Field(
        default_factory=list,
        description="Detected QR codes"
    )
    blocks: List[Block] = Field(
        default_factory=list,
        description="Detected layout blocks with OCR results"
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="Full concatenated text (reading order)"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(default="healthy")
    tesseract_available: bool
    languages_available: List[str]
    version: str


class ErrorResponse(BaseModel):
    """Error response format."""
    
    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error details"
    )


class ModelInfo(BaseModel):
    """Information about a trained model."""
    
    name: str
    description: Optional[str]
    created_at: str
    accuracy: Optional[float]
    is_active: bool


class TrainingStatus(BaseModel):
    """Status of a training job."""
    
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0-100
    message: Optional[str]
    model_name: Optional[str]
