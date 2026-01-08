"""
Image Quality Gate Module

Performs early rejection of low-quality images to improve system accuracy.
Checks: blur, brightness, resolution, and rotation.
"""

import cv2
import numpy as np
from typing import Tuple


def check_blur(gray: np.ndarray, threshold: float = 120.0) -> Tuple[bool, float]:
    """
    Check image blur using Laplacian variance.
    Higher variance = sharper image.
    """
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var >= threshold, laplacian_var


def check_brightness(gray: np.ndarray, min_brightness: float = 70.0, max_brightness: float = 230.0) -> Tuple[bool, float]:
    """
    Check if image brightness is within acceptable range.
    Too dark or too bright = poor OCR quality.
    """
    mean_brightness = np.mean(gray)
    is_ok = min_brightness <= mean_brightness <= max_brightness
    return is_ok, mean_brightness


def check_resolution(img: np.ndarray, min_height: int = 1200, min_width: int = 800) -> Tuple[bool, Tuple[int, int]]:
    """
    Check if image resolution is sufficient for OCR.
    Prescription documents need adequate resolution.
    """
    h, w = img.shape[:2]
    is_ok = h >= min_height and w >= min_width
    return is_ok, (h, w)


def check_contrast(gray: np.ndarray, threshold: float = 30.0) -> Tuple[bool, float]:
    """
    Check image contrast using standard deviation.
    Low contrast = poor text visibility.
    """
    contrast = np.std(gray)
    return contrast >= threshold, contrast


def quality_check(img: np.ndarray) -> Tuple[bool, str, dict]:
    """
    Perform comprehensive image quality check.
    
    Args:
        img: Input image in BGR format
        
    Returns:
        Tuple of (is_acceptable, message, metrics)
    """
    if img is None or img.size == 0:
        return False, "Invalid or empty image", {}
    
    # Convert to grayscale for analysis
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    metrics = {}
    
    # Check blur
    blur_ok, blur_val = check_blur(gray)
    metrics["blur_score"] = round(blur_val, 2)
    if not blur_ok:
        return False, f"Image too blurry (score: {blur_val:.1f}, min: 120)", metrics
    
    # Check brightness
    bright_ok, bright_val = check_brightness(gray)
    metrics["brightness"] = round(bright_val, 2)
    if not bright_ok:
        if bright_val < 70:
            return False, f"Image too dark (brightness: {bright_val:.1f})", metrics
        else:
            return False, f"Image too bright (brightness: {bright_val:.1f})", metrics
    
    # Check resolution
    res_ok, (h, w) = check_resolution(img)
    metrics["resolution"] = {"height": h, "width": w}
    if not res_ok:
        return False, f"Low resolution ({w}x{h}, min: 800x1200)", metrics
    
    # Check contrast
    contrast_ok, contrast_val = check_contrast(gray)
    metrics["contrast"] = round(contrast_val, 2)
    if not contrast_ok:
        return False, f"Low contrast (score: {contrast_val:.1f}, min: 30)", metrics
    
    return True, "Image quality acceptable", metrics


def quality_check_lenient(img: np.ndarray) -> Tuple[bool, str, dict]:
    """
    Lenient quality check for mobile-captured images.
    Uses lower thresholds but still rejects unusable images.
    """
    if img is None or img.size == 0:
        return False, "Invalid or empty image", {}
    
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    metrics = {}
    
    # Lenient blur check
    blur_ok, blur_val = check_blur(gray, threshold=80.0)
    metrics["blur_score"] = round(blur_val, 2)
    if not blur_ok:
        return False, f"Image too blurry for OCR (score: {blur_val:.1f})", metrics
    
    # Lenient brightness check
    bright_ok, bright_val = check_brightness(gray, min_brightness=50.0, max_brightness=240.0)
    metrics["brightness"] = round(bright_val, 2)
    if not bright_ok:
        return False, f"Image brightness outside acceptable range", metrics
    
    # Lenient resolution check
    res_ok, (h, w) = check_resolution(img, min_height=600, min_width=400)
    metrics["resolution"] = {"height": h, "width": w}
    if not res_ok:
        return False, f"Resolution too low for accurate OCR", metrics
    
    return True, "Image quality acceptable (lenient mode)", metrics

