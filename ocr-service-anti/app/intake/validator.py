"""
Layer 1: Image Intake & Validation

Purpose: Ensure image is processable before OCR
- Validate image format (jpg, png, webp, etc.)
- Check resolution (≥150 DPI, prefer 300 DPI)
- Detect and correct orientation (EXIF)
- Validate color mode (RGB/grayscale)
- Reject corrupted, too-small, or fully blurred images
"""

import io
from typing import Tuple, Optional

import numpy as np
from PIL import Image, ExifTags, UnidentifiedImageError
import cv2

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import (
    ImageValidationError,
    UnsupportedFormatError,
    ImageTooSmallError,
    ImageCorruptedError,
    LowResolutionError,
)

logger = get_logger(__name__)


class ImageValidator:
    """
    Validates and prepares images for OCR processing.
    
    This is the gatekeeping layer - no OCR happens here.
    Only images that pass validation proceed to the next layer.
    """
    
    def __init__(self):
        self.supported_formats = set(settings.supported_formats)
        self.min_width = settings.min_image_width
        self.min_height = settings.min_image_height
        self.max_size_bytes = int(settings.max_image_size_mb * 1024 * 1024)
        self.min_dpi = settings.min_dpi
    
    def validate(self, context) -> 'PipelineContext':
        """
        Validate image and prepare it for processing.
        
        Args:
            context: PipelineContext with image_bytes
        
        Returns:
            Updated context with pil_image and cv_image
        
        Raises:
            ImageValidationError: If image fails validation
        """
        logger.info(f"Validating image: {context.filename}")
        
        # Check file size
        self._check_file_size(context.image_bytes)
        
        # Load and validate image
        pil_image = self._load_image(context.image_bytes)
        
        # Check format
        self._check_format(pil_image, context.filename)
        
        # Check dimensions
        self._check_dimensions(pil_image)
        
        # Fix orientation from EXIF
        pil_image = self._fix_orientation(pil_image)
        
        # Convert to CV2 format
        cv_image = self._pil_to_cv2(pil_image)
        
        # Check for completely black/white images
        self._check_not_blank(cv_image)
        
        # Update context
        context.pil_image = pil_image
        context.cv_image = cv_image
        
        logger.info(
            f"Validation passed: {pil_image.size[0]}x{pil_image.size[1]}, "
            f"mode={pil_image.mode}"
        )
        
        return context
    
    def _check_file_size(self, image_bytes: bytes) -> None:
        """Check if file size is within limits."""
        size = len(image_bytes)
        if size > self.max_size_bytes:
            raise ImageValidationError(
                message=f"Image too large: {size / 1024 / 1024:.1f}MB",
                details={
                    "size_bytes": size,
                    "max_bytes": self.max_size_bytes
                }
            )
    
    def _load_image(self, image_bytes: bytes) -> Image.Image:
        """Load image from bytes."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            # Force load to catch corruption
            img.load()
            return img
        except UnidentifiedImageError:
            raise ImageCorruptedError(
                message="Cannot identify image file - may be corrupted"
            )
        except Exception as e:
            raise ImageCorruptedError(
                message=f"Failed to load image: {str(e)}"
            )
    
    def _check_format(self, image: Image.Image, filename: str) -> None:
        """Check if image format is supported."""
        # Get format from PIL
        fmt = image.format
        if fmt:
            fmt = fmt.lower()
        
        # Also check filename extension
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        
        # Normalize format names
        format_map = {
            "jpeg": "jpg",
            "tif": "tiff",
        }
        fmt = format_map.get(fmt, fmt)
        ext = format_map.get(ext, ext)
        
        if fmt not in self.supported_formats and ext not in self.supported_formats:
            raise UnsupportedFormatError(
                message=f"Unsupported image format: {fmt or ext}",
                details={
                    "format": fmt,
                    "extension": ext,
                    "supported": list(self.supported_formats)
                }
            )
    
    def _check_dimensions(self, image: Image.Image) -> None:
        """Check if image dimensions are sufficient."""
        width, height = image.size
        
        if width < self.min_width or height < self.min_height:
            raise ImageTooSmallError(
                message=f"Image too small: {width}x{height}",
                details={
                    "width": width,
                    "height": height,
                    "min_width": self.min_width,
                    "min_height": self.min_height
                }
            )
    
    def _fix_orientation(self, image: Image.Image) -> Image.Image:
        """Fix image orientation based on EXIF data."""
        try:
            # Get EXIF orientation
            exif = image.getexif()
            if not exif:
                return image
            
            # Find orientation tag
            orientation_key = None
            for key, val in ExifTags.TAGS.items():
                if val == "Orientation":
                    orientation_key = key
                    break
            
            if orientation_key is None or orientation_key not in exif:
                return image
            
            orientation = exif[orientation_key]
            
            # Apply rotation/flip based on orientation
            rotations = {
                3: Image.Transpose.ROTATE_180,
                6: Image.Transpose.ROTATE_270,
                8: Image.Transpose.ROTATE_90,
            }
            
            if orientation in rotations:
                logger.debug(f"Fixing orientation: {orientation}")
                image = image.transpose(rotations[orientation])
            
            # Handle flipped orientations
            if orientation in [2, 4, 5, 7]:
                image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            
            return image
            
        except Exception as e:
            logger.warning(f"Could not fix orientation: {e}")
            return image
    
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format (BGR or grayscale)."""
        # Convert to RGB if needed
        if pil_image.mode == "RGBA":
            # Create white background for transparency
            background = Image.new("RGB", pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.split()[3])
            pil_image = background
        elif pil_image.mode == "P":
            pil_image = pil_image.convert("RGB")
        elif pil_image.mode == "L":
            # Already grayscale
            return np.array(pil_image)
        elif pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        
        # Convert to numpy array
        rgb_array = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        
        return bgr_array
    
    def _check_not_blank(self, cv_image: np.ndarray) -> None:
        """Check if image is not completely blank (all black or all white)."""
        # Convert to grayscale if needed
        if len(cv_image.shape) == 3:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_image
        
        # Check for all black or all white
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        
        if std_val < 5:  # Very uniform image
            if mean_val < 10:
                raise ImageValidationError(
                    message="Image appears to be blank (all black)"
                )
            elif mean_val > 245:
                raise ImageValidationError(
                    message="Image appears to be blank (all white)"
                )
    
    def get_dpi(self, pil_image: Image.Image) -> Optional[int]:
        """Extract DPI from image metadata if available."""
        try:
            dpi = pil_image.info.get("dpi")
            if dpi:
                # Return average of x and y DPI
                return int((dpi[0] + dpi[1]) / 2)
        except Exception:
            pass
        return None
