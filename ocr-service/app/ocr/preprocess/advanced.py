"""
Advanced Image Preprocessing for Medical Prescriptions
Handles poor quality images, tables, handwriting, and complex layouts
"""
import cv2
import numpy as np
from typing import Tuple, List, Optional
from ...core.logger import logger


def enhance_contrast_clahe(image: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    Excellent for images with varying lighting conditions
    
    Args:
        image: Grayscale image
        
    Returns:
        Contrast-enhanced image
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def remove_shadows(image: np.ndarray) -> np.ndarray:
    """
    Remove shadows from image
    Useful for photos taken under poor lighting
    
    Args:
        image: BGR or grayscale image
        
    Returns:
        Shadow-removed image
    """
    if len(image.shape) == 3:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply morphological operation to get illumination
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        illumination = cv2.morphologyEx(l, cv2.MORPH_CLOSE, kernel)
        
        # Remove illumination
        corrected = cv2.divide(l, illumination, scale=255)
        
        # Merge back
        lab = cv2.merge([corrected, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        l = image
        
        # Apply morphological operation to get illumination
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        illumination = cv2.morphologyEx(l, cv2.MORPH_CLOSE, kernel)
        
        # Remove illumination
        corrected = cv2.divide(l, illumination, scale=255)
        
        return corrected


def remove_noise_advanced(image: np.ndarray) -> np.ndarray:
    """
    Advanced noise removal while preserving text edges
    Combines bilateral filter and morphological operations
    
    Args:
        image: Grayscale image
        
    Returns:
        Denoised image
    """
    # Bilateral filter - smooths while keeping edges sharp
    denoised = cv2.bilateralFilter(image, 9, 75, 75)
    
    # Morphological opening to remove small noise
    kernel = np.ones((2, 2), np.uint8)
    opened = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel, iterations=1)
    
    return opened


def deskew_image_advanced(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Advanced deskewing using projection profile
    Better for tables and structured documents
    
    Args:
        image: Binary image
        
    Returns:
        Tuple of (deskewed image, angle in degrees)
    """
    # Compute angle using Hough Line Transform
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    
    if lines is None:
        return image, 0.0
    
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 != 0:
            angle = np.degrees(np.arctan((y2 - y1) / (x2 - x1)))
            if abs(angle) < 45:  # Only consider reasonable angles
                angles.append(angle)
    
    if not angles:
        return image, 0.0
    
    median_angle = np.median(angles)
    
    # Only rotate if angle is significant
    if abs(median_angle) < 0.5:
        return image, 0.0
    
    # Rotate image
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    
    # Calculate new image size to avoid cropping
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    
    # Adjust rotation matrix
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]
    
    rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    logger.info(f"Image deskewed by {median_angle:.2f} degrees")
    
    return rotated, median_angle


def enhance_table_lines(image: np.ndarray) -> np.ndarray:
    """
    Enhance table lines for better table detection
    
    Args:
        image: Grayscale image
        
    Returns:
        Image with enhanced lines
    """
    # Detect horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    
    # Detect lines
    horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    # Combine lines
    table_lines = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0)
    
    # Combine with original
    enhanced = cv2.addWeighted(image, 0.7, table_lines, 0.3, 0)
    
    return enhanced


def remove_borders(image: np.ndarray, border_size: int = 10) -> np.ndarray:
    """
    Remove borders from image (useful for scanned documents)
    
    Args:
        image: Input image
        border_size: Size of border to remove in pixels
        
    Returns:
        Image with borders removed
    """
    h, w = image.shape[:2]
    return image[border_size:h-border_size, border_size:w-border_size]


def adaptive_binarization(image: np.ndarray, method: str = 'gaussian') -> np.ndarray:
    """
    Advanced adaptive thresholding with multiple methods
    
    Args:
        image: Grayscale image
        method: 'gaussian', 'mean', or 'otsu'
        
    Returns:
        Binary image
    """
    if method == 'otsu':
        # Otsu's thresholding
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == 'mean':
        # Adaptive mean thresholding
        binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
    else:  # gaussian
        # Adaptive gaussian thresholding (default, best for prescriptions)
        binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
    
    return binary


def upscale_image(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
    """
    Upscale image for better OCR accuracy on small text
    
    Args:
        image: Input image
        scale: Scale factor (2.0 = double size)
        
    Returns:
        Upscaled image
    """
    height, width = image.shape[:2]
    new_dim = (int(width * scale), int(height * scale))
    
    # Use INTER_CUBIC for upscaling (better quality)
    upscaled = cv2.resize(image, new_dim, interpolation=cv2.INTER_CUBIC)
    
    return upscaled


def preprocess_for_medical_ocr(
    image: np.ndarray,
    remove_shadow: bool = True,
    deskew: bool = True,
    enhance_contrast: bool = True,
    denoise: bool = True,
    upscale: bool = True,
    upscale_factor: float = 1.5
) -> np.ndarray:
    """
    Complete preprocessing pipeline for medical prescription images
    Optimized for poor quality, handwritten text, and complex tables
    
    Args:
        image: Input BGR image
        remove_shadow: Remove shadows and lighting artifacts
        deskew: Straighten tilted images
        enhance_contrast: Enhance contrast with CLAHE
        denoise: Remove noise while preserving text
        upscale: Upscale image for better OCR on small text
        upscale_factor: Scale factor for upscaling
        
    Returns:
        Preprocessed image ready for OCR
    """
    logger.info("Starting advanced preprocessing for medical prescription")
    
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Step 1: Upscale if needed (do this first for better quality)
    if upscale and upscale_factor > 1.0:
        gray = upscale_image(gray, upscale_factor)
        logger.info(f"Image upscaled by {upscale_factor}x to {gray.shape}")
    
    # Step 2: Remove shadows
    if remove_shadow:
        gray = remove_shadows(gray)
        logger.info("Shadows removed")
    
    # Step 3: Enhance contrast
    if enhance_contrast:
        gray = enhance_contrast_clahe(gray)
        logger.info("Contrast enhanced with CLAHE")
    
    # Step 4: Denoise
    if denoise:
        gray = remove_noise_advanced(gray)
        logger.info("Noise removed with bilateral filter")
    
    # Step 5: Binarization
    binary = adaptive_binarization(gray, method='gaussian')
    logger.info("Adaptive binarization applied")
    
    # Step 6: Deskew
    if deskew:
        binary, angle = deskew_image_advanced(binary)
        if abs(angle) > 0.5:
            logger.info(f"Image deskewed by {angle:.2f} degrees")
    
    # Step 7: Enhance table lines (helps with table detection)
    binary = enhance_table_lines(binary)
    logger.info("Table lines enhanced")
    
    # Step 8: Morphological operations to clean up
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    logger.info("Advanced preprocessing completed")
    
    return binary


def preprocess_for_table_detection(image: np.ndarray) -> np.ndarray:
    """
    Specialized preprocessing for detecting table structures
    
    Args:
        image: Input image
        
    Returns:
        Image optimized for table detection
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Invert if needed (tables should be black lines on white)
    if np.mean(binary) < 127:
        binary = cv2.bitwise_not(binary)
    
    return binary
