"""
OCR Output Contract - System Backbone
Defines the structure that LLM service will consume
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class BlockType(str, Enum):
    """Document block classification types"""
    HEADER = "header"
    BODY = "body"
    TABLE = "table"
    TABLE_HEADER = "table_header"
    TABLE_ROW = "table_row"
    FOOTER = "footer"
    MEDICATION = "medication"
    DOSAGE = "dosage"
    PATIENT_INFO = "patient_info"
    DOCTOR_INFO = "doctor_info"
    UNKNOWN = "unknown"


class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    KHMER = "kh"
    FRENCH = "fr"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class BoundingBox(BaseModel):
    """Coordinates for text block location"""
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def center_y(self) -> int:
        return (self.y1 + self.y2) // 2

    @property
    def center_x(self) -> int:
        return (self.x1 + self.x2) // 2


class OCRBlock(BaseModel):
    """Single text block with metadata"""
    text: str
    box: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0)
    block_type: BlockType = BlockType.UNKNOWN
    language: Optional[Language] = None
    line_number: Optional[int] = None
    group_id: Optional[int] = None  # For grouping related blocks


class TableCell(BaseModel):
    """Single cell in a table"""
    text: str
    row: int
    col: int
    confidence: float = Field(ge=0.0, le=1.0)
    box: Optional[BoundingBox] = None


class TableData(BaseModel):
    """Structured table data extracted from prescription"""
    headers: List[str] = []
    rows: List[List[str]] = []
    cells: List[TableCell] = []
    row_count: int = 0
    col_count: int = 0


class DosageSchedule(BaseModel):
    """Dosage schedule extracted from prescription"""
    morning: Optional[float] = None
    noon: Optional[float] = None
    afternoon: Optional[float] = None
    evening: Optional[float] = None
    night: Optional[float] = None


class ExtractedMedication(BaseModel):
    """Single medication extracted from prescription"""
    sequence: int = 1
    name: str
    strength: Optional[str] = None
    quantity: Optional[int] = None
    quantity_unit: Optional[str] = None
    dosage_schedule: Optional[DosageSchedule] = None
    instructions: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class PatientInfo(BaseModel):
    """Patient information from prescription"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_id: Optional[str] = None


class PrescriptionHeader(BaseModel):
    """Header information from prescription"""
    hospital_name: Optional[str] = None
    prescription_number: Optional[str] = None
    date: Optional[str] = None
    department: Optional[str] = None
    doctor_name: Optional[str] = None
    diagnosis: Optional[str] = None


class StructuredPrescription(BaseModel):
    """Complete structured prescription data"""
    header: Optional[PrescriptionHeader] = None
    patient: Optional[PatientInfo] = None
    medications: List[ExtractedMedication] = []
    table_data: Optional[TableData] = None
    notes: Optional[str] = None


class OCRResult(BaseModel):
    """Complete OCR output for a document"""
    # Raw OCR data
    raw_text: str = ""
    blocks: List[OCRBlock] = []

    # Language detection
    primary_language: Language = Language.UNKNOWN
    detected_languages: List[Language] = []

    # Structured extraction
    structured_data: Optional[StructuredPrescription] = None

    # Table detection
    tables: List[TableData] = []

    # Confidence metrics
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    low_confidence_blocks: List[int] = []  # Indices of blocks needing review

    # Processing metadata
    processing_time_ms: int = 0
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    needs_manual_review: bool = False

    # Warnings and errors
    warnings: List[str] = []
    errors: List[str] = []


class OCRRequest(BaseModel):
    """Request model for OCR processing"""
    languages: List[Language] = [Language.ENGLISH, Language.KHMER, Language.FRENCH]
    detect_tables: bool = True
    extract_medications: bool = True
    lenient_quality: bool = False


class OCRResponse(BaseModel):
    """Response model for OCR API"""
    success: bool
    result: Optional[OCRResult] = None
    error: Optional[str] = None
