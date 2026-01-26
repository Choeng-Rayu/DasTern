"""
Document Layout Analysis Module

Splits prescription documents into OCR-safe regions.
Handles: text blocks, headers, medication tables, signatures.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RegionType(str, Enum):
    HEADER = "header"
    BODY = "body"
    TABLE = "table"
    SIGNATURE = "signature"
    FOOTER = "footer"
    UNKNOWN = "unknown"


@dataclass
class Region:
    box: Tuple[int, int, int, int]  # x, y, w, h
    region_type: RegionType
    confidence: float = 1.0


def extract_regions(img: np.ndarray, min_height: int = 50, min_width: int = 120) -> List[Dict]:
    """
    Extract text regions from preprocessed document image.
    
    Args:
        img: Binary/grayscale preprocessed image
        min_height: Minimum region height to consider
        min_width: Minimum region width to consider
        
    Returns:
        List of region dictionaries with box coordinates and type
    """
    # Ensure binary image
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    if np.mean(img) > 127:
        # Invert if white background (we need text as white for contour detection)
        work_img = cv2.bitwise_not(img)
    else:
        work_img = img.copy()
    
    # Dilate to merge nearby text into blocks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilated = cv2.dilate(work_img, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    img_height, img_width = img.shape[:2]
    regions = []
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by size
        if h < min_height or w < min_width:
            continue
        
        # Classify region based on position
        region_type = classify_region(x, y, w, h, img_width, img_height)
        
        regions.append({
            "box": (x, y, w, h),
            "type": region_type,
            "area": w * h
        })
    
    # Sort regions top-to-bottom, left-to-right
    regions.sort(key=lambda r: (r["box"][1], r["box"][0]))
    
    return regions


def classify_region(x: int, y: int, w: int, h: int, img_w: int, img_h: int) -> str:
    """
    Classify region type based on position and size heuristics.
    """
    # Header: top 15% of document
    if y < img_h * 0.15:
        return RegionType.HEADER.value
    
    # Footer: bottom 10% of document
    if y + h > img_h * 0.90:
        return RegionType.FOOTER.value
    
    # Signature: bottom-right area, typically small
    if y > img_h * 0.75 and x > img_w * 0.5:
        return RegionType.SIGNATURE.value
    
    # Table detection: wide regions with specific aspect ratio
    aspect_ratio = w / h if h > 0 else 0
    if aspect_ratio > 3 and w > img_w * 0.6:
        return RegionType.TABLE.value
    
    return RegionType.BODY.value


def extract_text_lines(img: np.ndarray, region_box: Tuple[int, int, int, int]) -> List[Dict]:
    """
    Extract individual text lines within a region.
    Useful for line-by-line OCR processing.
    """
    x, y, w, h = region_box
    roi = img[y:y+h, x:x+w]
    
    if len(roi.shape) == 3:
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Invert if needed
    if np.mean(roi) > 127:
        work_roi = cv2.bitwise_not(roi)
    else:
        work_roi = roi.copy()
    
    # Horizontal projection profile
    horizontal_proj = np.sum(work_roi, axis=1)
    
    # Find line boundaries
    threshold = np.max(horizontal_proj) * 0.1
    lines = []
    in_line = False
    line_start = 0
    
    for i, val in enumerate(horizontal_proj):
        if val > threshold and not in_line:
            in_line = True
            line_start = i
        elif val <= threshold and in_line:
            in_line = False
            if i - line_start > 10:  # Minimum line height
                lines.append({
                    "box": (x, y + line_start, w, i - line_start),
                    "relative_box": (0, line_start, w, i - line_start)
                })
    
    # Handle last line
    if in_line and len(horizontal_proj) - line_start > 10:
        lines.append({
            "box": (x, y + line_start, w, len(horizontal_proj) - line_start),
            "relative_box": (0, line_start, w, len(horizontal_proj) - line_start)
        })
    
    return lines


def merge_overlapping_regions(regions: List[Dict], overlap_threshold: float = 0.5) -> List[Dict]:
    """
    Merge overlapping or very close regions.
    """
    if not regions:
        return []
    
    merged = []
    used = set()
    
    for i, r1 in enumerate(regions):
        if i in used:
            continue
        
        x1, y1, w1, h1 = r1["box"]
        
        for j, r2 in enumerate(regions[i+1:], i+1):
            if j in used:
                continue
            
            x2, y2, w2, h2 = r2["box"]
            
            # Check vertical overlap
            if abs(y1 - y2) < min(h1, h2) * overlap_threshold:
                # Merge
                new_x = min(x1, x2)
                new_y = min(y1, y2)
                new_w = max(x1 + w1, x2 + w2) - new_x
                new_h = max(y1 + h1, y2 + h2) - new_y
                
                r1["box"] = (new_x, new_y, new_w, new_h)
                r1["area"] = new_w * new_h
                used.add(j)
        
        merged.append(r1)
    
    return merged

