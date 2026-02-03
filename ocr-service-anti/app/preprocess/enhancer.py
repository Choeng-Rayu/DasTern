"""
Layer 3: Image Preprocessing & Enhancement

Purpose: Improve OCR accuracy before Tesseract
- De-skew
- Adaptive thresholding
- Contrast stretching (CLAHE)
- Sharpening (for handwriting/stamps)
- Noise removal (morphological operations)
- Resize to optimal DPI

Rule: NEVER destroy text just to make it pretty.
Preprocessing is dynamic, based on Layer 2 output.
"""

import numpy as np
import cv2
from typing import Optional, Tuple

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import PreprocessingError

logger = get_logger(__name__)


class ImageEnhancer:
    """
    Enhances images for optimal OCR accuracy.
    
    Applies preprocessing dynamically based on quality analysis results.
    Conservative approach - avoid destroying text.
    """
    
    def __init__(self):
        self.preferred_dpi = settings.preferred_dpi
        self.max_skew_angle = settings.max_skew_angle
    
    def enhance(self, context) -> 'PipelineContext':
        """
        Enhance image based on quality analysis.
        
        Args:
            context: PipelineContext with cv_image and quality_metrics
        
        Returns:
            Updated context with preprocessed_image
        """
        logger.info("Preprocessing image")
        
        image = context.cv_image.copy()
        quality = context.quality_metrics or {}
        
        try:
            # Step 1: Deskew if needed
            if quality.get("needs_deskew", False):
                skew_angle = quality.get("skew_angle", 0)
                if abs(skew_angle) > 0.5 and abs(skew_angle) < self.max_skew_angle:
                    image = self._deskew(image, skew_angle)
                    logger.debug(f"Deskewed by {skew_angle:.2f}°")
            
            # Step 2: Convert to grayscale for processing
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Step 3: Denoise if needed (before contrast enhancement)
            if quality.get("needs_denoising", False):
                gray = self._denoise(gray)
                logger.debug("Applied denoising")
            
            # Step 4: Enhance contrast if needed
            if quality.get("needs_contrast_enhancement", False):
                gray = self._enhance_contrast(gray)
                logger.debug("Enhanced contrast with CLAHE")
            
            # Step 5: Sharpen if image is blurry
            if quality.get("needs_sharpening", False):
                gray = self._sharpen(gray)
                logger.debug("Applied sharpening")
            
            # Step 6: Adaptive thresholding for binarization
            # Keep both versions - original gray and binarized
            binary = self._adaptive_threshold(gray)
            
            # Step 7: Clean up with morphological operations
            binary = self._morphological_cleanup(binary)
            
            # Store both versions in context
            context.preprocessed_image = gray  # Keep grayscale for OCR
            context.binary_image = binary  # Binary for layout detection
            
            logger.info(f"Preprocessing complete: {gray.shape}")
            
            return context
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            raise PreprocessingError(
                message=f"Image preprocessing failed: {str(e)}"
            )
    
    def _deskew(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image to correct skew.
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Negative angle to correct the skew
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new image bounds
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # Adjust rotation matrix for new bounds
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        # Apply rotation with white background
        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255) if len(image.shape) == 3 else 255
        )
        
        return rotated
    
    def _denoise(self, gray: np.ndarray) -> np.ndarray:
        """
        Remove noise while preserving text edges.
        Uses Non-local Means Denoising.
        """
        # Conservative denoising to preserve text
        denoised = cv2.fastNlMeansDenoising(
            gray,
            h=10,  # Filter strength (lower = preserve more detail)
            templateWindowSize=7,
            searchWindowSize=21
        )
        return denoised
    
    def _enhance_contrast(self, gray: np.ndarray) -> np.ndarray:
        """
        Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
        Better than regular histogram equalization for documents.
        """
        clahe = cv2.createCLAHE(
            clipLimit=2.0,  # Limit contrast amplification
            tileGridSize=(8, 8)
        )
        enhanced = clahe.apply(gray)
        return enhanced
    
    def _sharpen(self, gray: np.ndarray) -> np.ndarray:
        """
        Sharpen image using unsharp masking.
        Helps with slightly blurry text and stamps.
        """
        # Create Gaussian blur
        blurred = cv2.GaussianBlur(gray, (0, 0), 3)
        
        # Unsharp mask: original + (original - blurred) * amount
        sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        
        return sharpened
    
    def _adaptive_threshold(self, gray: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for binarization.
        Works well with varying lighting conditions.
        """
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,  # Size of neighborhood
            C=2  # Constant subtracted from mean
        )
        return binary
    
    def _morphological_cleanup(self, binary: np.ndarray) -> np.ndarray:
        """
        Clean up binary image using morphological operations.
        Remove small noise while preserving text.
        """
        # Small kernel to remove noise without affecting text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        
        # Opening (erosion followed by dilation) removes small noise
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Closing (dilation followed by erosion) fills small holes
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def resize_to_dpi(
        self, 
        image: np.ndarray, 
        current_dpi: Optional[int], 
        target_dpi: int = 300
    ) -> np.ndarray:
        """
        Resize image to target DPI if current DPI is known and lower.
        """
        if current_dpi is None or current_dpi >= target_dpi:
            return image
        
        scale = target_dpi / current_dpi
        h, w = image.shape[:2]
        new_size = (int(w * scale), int(h * scale))
        
        # Use INTER_CUBIC for upscaling
        resized = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
        
        logger.debug(f"Resized from {w}x{h} to {new_size[0]}x{new_size[1]}")
        
        return resized
