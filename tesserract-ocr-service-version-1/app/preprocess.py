"""
Advanced OpenCV Preprocessing Module

Prepares images for optimal OCR accuracy.
Includes: bilateral filtering, CLAHE, adaptive thresholding, deskewing.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def apply_bilateral_filter(img: np.ndarray, d: int = 9, sigma_color: int = 75, sigma_space: int = 75) -> np.ndarray:
    """
    Apply bilateral filter to reduce noise while preserving edges.
    Critical for document text clarity.
    """
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)


def apply_clahe(img: np.ndarray, clip_limit: float = 2.0, tile_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Improves local contrast for better text visibility.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    return clahe.apply(img)


def apply_adaptive_threshold(img: np.ndarray, block_size: int = 15, c: int = 3) -> np.ndarray:
    """
    Apply adaptive thresholding for binarization.
    Handles varying lighting conditions across the document.
    """
    return cv2.adaptiveThreshold(
        img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size, c
    )


def deskew(img: np.ndarray, max_angle: float = 45.0) -> np.ndarray:
    """
    Detect and correct document skew/rotation.
    Essential for accurate line detection and OCR.
    """
    # Find non-zero pixels (text regions)
    coords = cv2.findNonZero(cv2.bitwise_not(img) if np.mean(img) > 127 else img)
    
    if coords is None or len(coords) < 10:
        return img
    
    # Get rotation angle from minimum area rectangle
    angle = cv2.minAreaRect(coords)[-1]
    
    # Adjust angle based on rectangle orientation
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # Limit correction to reasonable range
    if abs(angle) > max_angle or abs(angle) < 0.5:
        return img
    
    # Apply rotation
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    return cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


def remove_noise(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Remove small noise particles using morphological operations.
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    # Opening removes small white noise
    opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    # Closing fills small black holes
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    return closed


def enhance_text(img: np.ndarray) -> np.ndarray:
    """
    Enhance text visibility using sharpening.
    """
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    return cv2.filter2D(img, -1, kernel)


def preprocess(img: np.ndarray, apply_deskew: bool = True, return_gray: bool = False) -> np.ndarray:
    """
    Full preprocessing pipeline for prescription images.
    
    Args:
        img: Input BGR image
        apply_deskew: Whether to apply deskew correction
        return_gray: If True, return grayscale instead of binary
        
    Returns:
        Preprocessed image ready for OCR
    """
    # Convert to grayscale if needed
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    # Step 1: Bilateral filter (noise reduction + edge preservation)
    filtered = apply_bilateral_filter(gray)
    
    # Step 2: CLAHE (contrast enhancement)
    contrast = apply_clahe(filtered)
    
    if return_gray:
        if apply_deskew:
            # For deskew, we need binary temporarily
            temp_binary = apply_adaptive_threshold(contrast)
            # Get deskew angle from binary
            coords = cv2.findNonZero(cv2.bitwise_not(temp_binary))
            if coords is not None and len(coords) >= 10:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                if 0.5 <= abs(angle) <= 45:
                    h, w = contrast.shape[:2]
                    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
                    contrast = cv2.warpAffine(contrast, M, (w, h),
                                             flags=cv2.INTER_CUBIC,
                                             borderMode=cv2.BORDER_REPLICATE)
        return contrast
    
    # Step 3: Adaptive thresholding (binarization)
    binary = apply_adaptive_threshold(contrast)
    
    # Step 4: Deskew if requested
    if apply_deskew:
        binary = deskew(binary)
    
    # Step 5: Noise removal
    cleaned = remove_noise(binary)
    
    return cleaned


def preprocess_for_khmer(img: np.ndarray) -> np.ndarray:
    """
    Specialized preprocessing for Khmer script.
    Khmer has complex diacritics that need careful handling.
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    # Gentler filtering for complex scripts
    filtered = cv2.bilateralFilter(gray, 5, 50, 50)
    
    # Less aggressive CLAHE
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(16, 16))
    contrast = clahe.apply(filtered)
    
    # Otsu's thresholding often works better for Khmer
    _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary

