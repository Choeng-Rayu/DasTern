"""
Image preprocessing using OpenCV
Goal: Improve OCR accuracy without destroying handwriting, tables, symbols
"""
import cv2
import numpy as np
from typing import Optional
from ...core.config import settings
from ...core.logger import logger


def preprocess_image(
    image: np.ndarray,
    denoise_strength: Optional[int] = None,
    block_size: Optional[int] = None,
    threshold_c: Optional[int] = None
) -> np.ndarray:
    """
    Preprocess image for OCR
    
    Steps:
    1. Convert to grayscale
    2. Denoise (light - to preserve text clarity)
    3. Adaptive thresholding (to handle varying lighting)
    
    Args:
        image: Input BGR image
        denoise_strength: Denoising filter strength (default from settings)
        block_size: Size of pixel neighborhood for adaptive threshold
        threshold_c: Constant subtracted from weighted mean
        
    Returns:
        Preprocessed binary image
    """
    # Use defaults from settings if not provided
    h = denoise_strength or settings.DENOISE_STRENGTH
    block = block_size or settings.ADAPTIVE_THRESHOLD_BLOCK_SIZE
    c = threshold_c or settings.ADAPTIVE_THRESHOLD_C
    
    logger.debug(f"Preprocessing image with: denoise={h}, block={block}, c={c}")
    
    # Step 1: Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Step 2: Denoise (light denoising to preserve details)
    denoise = cv2.fastNlMeansDenoising(gray, h=h)
    
    # Step 3: Adaptive threshold (handles varying lighting conditions)
    thresh = cv2.adaptiveThreshold(
        denoise, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block, c
    )
    
    return thresh


def preprocess_for_ocr(
    image: np.ndarray,
    apply_preprocessing: bool = True
) -> np.ndarray:
    """
    Main preprocessing entry point
    
    Args:
        image: Input image (BGR or grayscale)
        apply_preprocessing: Whether to apply preprocessing
        
    Returns:
        Image ready for OCR
    """
    if not apply_preprocessing:
        return image
    
    return preprocess_image(image)


def deskew_image(image: np.ndarray, max_angle: float = 10.0) -> np.ndarray:
    """
    Deskew image if needed (light deskew only)
    
    Note: Aggressive deskew can damage table structures.
    Only use when text is clearly skewed.
    
    Args:
        image: Grayscale image
        max_angle: Maximum angle to correct
        
    Returns:
        Deskewed image
    """
    # Detect edges
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    
    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    if lines is None:
        return image
    
    # Calculate average angle
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 != 0:
            angle = np.degrees(np.arctan((y2 - y1) / (x2 - x1)))
            if abs(angle) < max_angle:
                angles.append(angle)
    
    if not angles:
        return image
    
    median_angle = np.median(angles)
    
    # Only deskew if angle is significant
    if abs(median_angle) < 0.5:
        return image
    
    # Rotate image
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(
        image, rotation_matrix, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    
    logger.debug(f"Image deskewed by {median_angle:.2f} degrees")
    
    return rotated
