"""
Layer 2: Image Quality Analysis

Purpose: Decide how aggressive preprocessing should be
- Blur detection (Laplacian variance)
- Noise level estimation
- Contrast analysis
- Skew angle detection

Output controls the preprocessing layer behavior.
"""

import numpy as np
import cv2
from typing import Dict, Any, Tuple

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import QualityAnalysisError, ImageTooBlurryError

logger = get_logger(__name__)


class QualityAnalyzer:
    """
    Analyzes image quality to guide preprocessing decisions.
    
    This layer determines:
    - How blurry the image is
    - Contrast quality
    - Skew angle
    - Whether image needs enhancement
    """
    
    def __init__(self):
        self.blur_threshold_low = settings.blur_threshold_low
        self.blur_threshold_high = settings.blur_threshold_high
        self.contrast_threshold_low = settings.contrast_threshold_low
        self.contrast_threshold_high = settings.contrast_threshold_high
    
    def analyze(self, context) -> 'PipelineContext':
        """
        Analyze image quality metrics.
        
        Args:
            context: PipelineContext with cv_image
        
        Returns:
            Updated context with quality_metrics
        """
        logger.info("Analyzing image quality")
        
        cv_image = context.cv_image
        
        # Convert to grayscale for analysis
        if len(cv_image.shape) == 3:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_image
        
        # Analyze blur
        blur_score = self._calculate_blur_score(gray)
        blur_level = self._classify_blur(blur_score)
        
        # Analyze contrast
        contrast_score = self._calculate_contrast_score(gray)
        contrast_level = self._classify_contrast(contrast_score)
        
        # Detect skew angle
        skew_angle = self._detect_skew_angle(gray)
        
        # Estimate DPI if not available
        dpi = None
        if context.pil_image:
            from app.intake.validator import ImageValidator
            dpi = ImageValidator().get_dpi(context.pil_image)
        
        # Check for grayscale
        is_grayscale = len(cv_image.shape) == 2 or cv_image.shape[2] == 1
        
        # Estimate noise level
        noise_level = self._estimate_noise(gray)
        
        # Build quality metrics
        context.quality_metrics = {
            "blur": blur_level,
            "blur_score": blur_score,
            "contrast": contrast_level,
            "contrast_score": contrast_score,
            "skew_angle": skew_angle,
            "dpi": dpi,
            "is_grayscale": is_grayscale,
            "noise_level": noise_level,
            "needs_deskew": abs(skew_angle) > 0.5,
            "needs_contrast_enhancement": contrast_level == "low",
            "needs_denoising": noise_level > 10,
            "needs_sharpening": blur_level in ["medium", "high"],
        }
        
        logger.info(
            f"Quality analysis: blur={blur_level} ({blur_score:.1f}), "
            f"contrast={contrast_level} ({contrast_score:.1f}), "
            f"skew={skew_angle:.2f}°"
        )
        
        # Reject extremely blurry images
        if blur_level == "high" and blur_score < self.blur_threshold_high / 2:
            raise ImageTooBlurryError(
                message="Image is too blurry for reliable OCR",
                details={"blur_score": blur_score, "threshold": self.blur_threshold_high}
            )
        
        return context
    
    def _calculate_blur_score(self, gray: np.ndarray) -> float:
        """
        Calculate blur score using Laplacian variance.
        Higher score = sharper image.
        """
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return float(variance)
    
    def _classify_blur(self, score: float) -> str:
        """Classify blur level from score."""
        if score >= self.blur_threshold_low:
            return "low"  # Good, sharp image
        elif score >= self.blur_threshold_high:
            return "medium"
        else:
            return "high"  # Very blurry
    
    def _calculate_contrast_score(self, gray: np.ndarray) -> float:
        """
        Calculate contrast score using standard deviation.
        Higher score = more contrast.
        """
        return float(np.std(gray))
    
    def _classify_contrast(self, score: float) -> str:
        """Classify contrast level from score."""
        if score < self.contrast_threshold_low:
            return "low"
        elif score > self.contrast_threshold_high:
            return "high"  # Might be oversaturated
        else:
            return "ok"
    
    def _detect_skew_angle(self, gray: np.ndarray) -> float:
        """
        Detect document skew angle using Hough transform.
        Returns angle in degrees.
        """
        try:
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough transform
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi / 180,
                threshold=100,
                minLineLength=100,
                maxLineGap=10
            )
            
            if lines is None or len(lines) == 0:
                return 0.0
            
            # Calculate angles
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 != 0:
                    angle = np.degrees(np.arctan((y2 - y1) / (x2 - x1)))
                    # Only consider near-horizontal lines
                    if abs(angle) < 45:
                        angles.append(angle)
            
            if not angles:
                return 0.0
            
            # Use median angle (robust to outliers)
            median_angle = float(np.median(angles))
            
            # Clamp to reasonable range
            return max(-45.0, min(45.0, median_angle))
            
        except Exception as e:
            logger.warning(f"Skew detection failed: {e}")
            return 0.0
    
    def _estimate_noise(self, gray: np.ndarray) -> float:
        """
        Estimate noise level using median absolute deviation.
        """
        try:
            # Apply Laplacian to detect noise
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Use MAD (Median Absolute Deviation) as robust estimator
            sigma = np.median(np.abs(laplacian)) / 0.6745
            
            return float(sigma)
        except Exception:
            return 0.0
    
    def get_preprocessing_recommendations(
        self, 
        quality_metrics: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Get preprocessing recommendations based on quality metrics.
        """
        return {
            "deskew": quality_metrics.get("needs_deskew", False),
            "enhance_contrast": quality_metrics.get("needs_contrast_enhancement", False),
            "denoise": quality_metrics.get("needs_denoising", False),
            "sharpen": quality_metrics.get("needs_sharpening", False),
        }
