"""
Custom exceptions for the OCR Service.
Provides a hierarchy of exceptions for each layer.
"""

from typing import Optional, Dict, Any


class OCRServiceError(Exception):
    """Base exception for all OCR service errors."""
    
    error_code: str = "OCR_ERROR"
    status_code: int = 500
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.details = details or {}
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# Layer 1: Image Intake & Validation Errors
class ImageValidationError(OCRServiceError):
    """Errors during image validation (Layer 1)."""
    error_code = "IMAGE_VALIDATION_ERROR"
    status_code = 400


class UnsupportedFormatError(ImageValidationError):
    """Image format is not supported."""
    error_code = "UNSUPPORTED_FORMAT"


class ImageTooSmallError(ImageValidationError):
    """Image dimensions are too small."""
    error_code = "IMAGE_TOO_SMALL"


class ImageCorruptedError(ImageValidationError):
    """Image file is corrupted or unreadable."""
    error_code = "IMAGE_CORRUPTED"


class LowResolutionError(ImageValidationError):
    """Image DPI is too low."""
    error_code = "LOW_RESOLUTION"


# Layer 2: Quality Analysis Errors
class QualityAnalysisError(OCRServiceError):
    """Errors during quality analysis (Layer 2)."""
    error_code = "QUALITY_ANALYSIS_ERROR"
    status_code = 422


class ImageTooBlurryError(QualityAnalysisError):
    """Image is too blurry for reliable OCR."""
    error_code = "IMAGE_TOO_BLURRY"


# Layer 3: Preprocessing Errors
class PreprocessingError(OCRServiceError):
    """Errors during image preprocessing (Layer 3)."""
    error_code = "PREPROCESSING_ERROR"
    status_code = 500


# Layer 4: Layout Detection Errors
class LayoutDetectionError(OCRServiceError):
    """Errors during layout analysis (Layer 4)."""
    error_code = "LAYOUT_DETECTION_ERROR"
    status_code = 500


# Layer 5: OCR Extraction Errors
class OCRExtractionError(OCRServiceError):
    """Errors during OCR extraction (Layer 5)."""
    error_code = "OCR_EXTRACTION_ERROR"
    status_code = 500


class TesseractNotFoundError(OCRExtractionError):
    """Tesseract executable not found."""
    error_code = "TESSERACT_NOT_FOUND"


class LanguageNotAvailableError(OCRExtractionError):
    """Requested language pack not available."""
    error_code = "LANGUAGE_NOT_AVAILABLE"


# Layer 6: Post-processing Errors
class PostProcessingError(OCRServiceError):
    """Errors during post-processing (Layer 6)."""
    error_code = "POST_PROCESSING_ERROR"
    status_code = 500


# Layer 7: JSON Builder Errors
class JSONBuilderError(OCRServiceError):
    """Errors during JSON output building (Layer 7)."""
    error_code = "JSON_BUILDER_ERROR"
    status_code = 500


# Training Errors
class TrainingError(OCRServiceError):
    """Errors during model training."""
    error_code = "TRAINING_ERROR"
    status_code = 500


class ModelNotFoundError(TrainingError):
    """Requested model not found."""
    error_code = "MODEL_NOT_FOUND"
    status_code = 404
