"""
Table Detection and Extraction for Medical Prescriptions
Detects and extracts table structures from prescription images
"""
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
from typing import List, Dict, Any, Tuple, Optional
from ...core.logger import logger


class TableCell:
    """Represents a single table cell"""
    def __init__(self, x: int, y: int, w: int, h: int, text: str = "", confidence: float = 0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.confidence = confidence
        self.row = -1
        self.col = -1
    
    def center(self) -> Tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)
    
    def contains_point(self, x: int, y: int) -> bool:
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h


def detect_table_lines(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detect horizontal and vertical lines in image
    
    Args:
        image: Binary image
        
    Returns:
        Tuple of (horizontal_lines, vertical_lines)
    """
    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
    vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    return horizontal_lines, vertical_lines


def find_table_intersections(horizontal_lines: np.ndarray, vertical_lines: np.ndarray) -> List[Tuple[int, int]]:
    """
    Find intersection points of horizontal and vertical lines
    
    Args:
        horizontal_lines: Binary image with horizontal lines
        vertical_lines: Binary image with vertical lines
        
    Returns:
        List of (x, y) coordinates of intersections
    """
    # Combine lines
    combined = cv2.bitwise_and(horizontal_lines, vertical_lines)
    
    # Find contours at intersections
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    intersections = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        center_x = x + w // 2
        center_y = y + h // 2
        intersections.append((center_x, center_y))
    
    return intersections


def detect_table_cells(image: np.ndarray, min_cell_area: int = 1000) -> List[TableCell]:
    """
    Detect table cell boundaries
    
    Args:
        image: Binary image
        min_cell_area: Minimum area for a valid cell
        
    Returns:
        List of TableCell objects
    """
    # Detect lines
    horizontal_lines, vertical_lines = detect_table_lines(image)
    
    # Combine lines to create table mask
    table_mask = cv2.bitwise_or(horizontal_lines, vertical_lines)
    
    # Invert to get cell regions
    cell_regions = cv2.bitwise_not(table_mask)
    
    # Find contours (each contour is a potential cell)
    contours, _ = cv2.findContours(cell_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        
        # Filter out noise and very small cells
        if area > min_cell_area and w > 20 and h > 10:
            cells.append(TableCell(x, y, w, h))
    
    logger.info(f"Detected {len(cells)} potential table cells")
    
    return cells


def assign_cell_positions(cells: List[TableCell], tolerance: int = 10) -> List[TableCell]:
    """
    Assign row and column positions to cells
    
    Args:
        cells: List of TableCell objects
        tolerance: Pixel tolerance for row/column alignment
        
    Returns:
        List of cells with row and col assigned
    """
    if not cells:
        return cells
    
    # Sort cells by y-coordinate (top to bottom)
    cells_sorted = sorted(cells, key=lambda c: c.y)
    
    # Group cells into rows
    rows = []
    current_row = [cells_sorted[0]]
    current_row_y = cells_sorted[0].y
    
    for cell in cells_sorted[1:]:
        if abs(cell.y - current_row_y) <= tolerance:
            current_row.append(cell)
        else:
            rows.append(current_row)
            current_row = [cell]
            current_row_y = cell.y
    rows.append(current_row)
    
    # Assign row numbers and sort cells within rows by x-coordinate
    for row_idx, row in enumerate(rows):
        row.sort(key=lambda c: c.x)
        for col_idx, cell in enumerate(row):
            cell.row = row_idx
            cell.col = col_idx
    
    logger.info(f"Organized cells into {len(rows)} rows")
    
    return cells


def extract_text_from_cells(
    image: np.ndarray,
    cells: List[TableCell],
    languages: str = "khm+eng+fra"
) -> List[TableCell]:
    """
    Extract text from each cell using OCR
    
    Args:
        image: Original image
        cells: List of TableCell objects with positions
        languages: OCR languages
        
    Returns:
        List of cells with text extracted
    """
    for cell in cells:
        try:
            # Add padding to avoid cutting text
            padding = 5
            x1 = max(0, cell.x - padding)
            y1 = max(0, cell.y - padding)
            x2 = min(image.shape[1], cell.x + cell.w + padding)
            y2 = min(image.shape[0], cell.y + cell.h + padding)
            
            # Extract cell region
            cell_img = image[y1:y2, x1:x2]
            
            # Skip if cell is too small
            if cell_img.shape[0] < 10 or cell_img.shape[1] < 10:
                continue
            
            # Run OCR on cell
            custom_config = f"--oem 3 --psm 6"
            data = pytesseract.image_to_data(
                cell_img,
                lang=languages,
                output_type=Output.DICT,
                config=custom_config
            )
            
            # Combine text from cell
            texts = []
            confidences = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i])
                if text and conf > 0:
                    texts.append(text)
                    confidences.append(conf)
            
            if texts:
                cell.text = ' '.join(texts)
                cell.confidence = sum(confidences) / len(confidences)
        
        except Exception as e:
            logger.warning(f"Failed to extract text from cell at ({cell.x}, {cell.y}): {e}")
            continue
    
    return cells


def extract_table_structure(
    image: np.ndarray,
    languages: str = "khm+eng+fra",
    min_cell_area: int = 1000
) -> Dict[str, Any]:
    """
    Extract complete table structure from image
    
    Args:
        image: Input image (grayscale or binary)
        languages: OCR languages
        min_cell_area: Minimum area for valid cells
        
    Returns:
        Dictionary with table structure and content
    """
    logger.info("Starting table extraction")
    
    # Ensure binary image
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Invert if needed (lines should be black)
    if np.mean(binary) < 127:
        binary = cv2.bitwise_not(binary)
    
    # Detect cells
    cells = detect_table_cells(binary, min_cell_area)
    
    if not cells:
        logger.warning("No table cells detected")
        return {
            "found_table": False,
            "rows": 0,
            "columns": 0,
            "cells": []
        }
    
    # Assign positions
    cells = assign_cell_positions(cells)
    
    # Extract text from cells
    cells = extract_text_from_cells(gray, cells, languages)
    
    # Convert to structured format
    max_row = max(cell.row for cell in cells) + 1 if cells else 0
    max_col = max(cell.col for cell in cells) + 1 if cells else 0
    
    # Create table grid
    table_grid = [[None for _ in range(max_col)] for _ in range(max_row)]
    
    for cell in cells:
        if cell.row >= 0 and cell.col >= 0:
            table_grid[cell.row][cell.col] = {
                "text": cell.text,
                "confidence": cell.confidence,
                "bbox": {
                    "x": cell.x,
                    "y": cell.y,
                    "w": cell.w,
                    "h": cell.h
                }
            }
    
    # Convert grid to list of rows
    table_rows = []
    for row_idx, row in enumerate(table_grid):
        row_data = []
        for col_idx, cell in enumerate(row):
            if cell:
                row_data.append(cell)
            else:
                row_data.append({
                    "text": "",
                    "confidence": 0,
                    "bbox": {"x": 0, "y": 0, "w": 0, "h": 0}
                })
        table_rows.append(row_data)
    
    logger.info(f"Extracted table with {max_row} rows and {max_col} columns")
    
    return {
        "found_table": True,
        "rows": max_row,
        "columns": max_col,
        "cells": [
            {
                "row": cell.row,
                "col": cell.col,
                "text": cell.text,
                "confidence": cell.confidence,
                "bbox": {"x": cell.x, "y": cell.y, "w": cell.w, "h": cell.h}
            }
            for cell in cells if cell.row >= 0 and cell.col >= 0
        ],
        "table_grid": table_rows
    }


def detect_tables_in_image(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect multiple tables in an image
    
    Args:
        image: Input image
        
    Returns:
        List of table regions with bounding boxes
    """
    # Convert to binary
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Detect lines
    horizontal_lines, vertical_lines = detect_table_lines(binary)
    
    # Combine lines
    table_mask = cv2.bitwise_or(horizontal_lines, vertical_lines)
    
    # Find table regions
    kernel = np.ones((20, 20), np.uint8)
    dilated = cv2.dilate(table_mask, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    tables = []
    for idx, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        
        # Filter out small regions
        if area > 10000 and w > 100 and h > 100:
            tables.append({
                "table_id": idx,
                "bbox": {"x": x, "y": y, "w": w, "h": h},
                "area": area
            })
    
    logger.info(f"Detected {len(tables)} table regions")
    
    return tables
