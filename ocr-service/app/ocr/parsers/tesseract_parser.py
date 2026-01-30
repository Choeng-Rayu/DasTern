"""
Tesseract OCR Output Parser
Converts raw Tesseract output to structured format with bounding boxes
"""
from typing import Dict, List, Any, Optional
from ...core.config import settings
from ...core.logger import logger


def parse_ocr_data(
    data: Dict[str, List],
    include_low_confidence: bool = True,
    min_confidence: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Parse raw Tesseract OCR output into structured format
    
    Args:
        data: Raw Tesseract output dictionary
        include_low_confidence: Include results with low confidence
        min_confidence: Minimum confidence threshold
        
    Returns:
        List of parsed OCR elements with text, bbox, and metadata
    """
    threshold = min_confidence if min_confidence is not None else settings.OCR_CONFIDENCE_THRESHOLD
    
    results = []
    n = len(data["text"])
    
    for i in range(n):
        text = data["text"][i].strip()
        
        # Skip empty text
        if not text:
            continue
        
        # Get confidence (Tesseract returns -1 for non-text elements)
        conf = int(data["conf"][i])
        
        # Skip if below threshold (unless we include all)
        if not include_low_confidence and conf < threshold and conf >= 0:
            continue
        
        # Build result object
        result = {
            "text": text,
            "confidence": conf,
            "bbox": {
                "x": data["left"][i],
                "y": data["top"][i],
                "w": data["width"][i],
                "h": data["height"][i],
            },
            "block": data["block_num"][i],
            "paragraph": data["par_num"][i],
            "line": data["line_num"][i],
            "word": data["word_num"][i],
        }
        
        results.append(result)
    
    logger.debug(f"Parsed {len(results)} text elements from {n} total elements")
    
    return results


def group_by_lines(results: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Group OCR results by line
    
    Args:
        results: Parsed OCR results
        
    Returns:
        List of lines, each containing word results
    """
    lines = {}
    
    for result in results:
        line_key = (result["block"], result["paragraph"], result["line"])
        if line_key not in lines:
            lines[line_key] = []
        lines[line_key].append(result)
    
    # Sort by position and return
    sorted_lines = sorted(lines.items(), key=lambda x: (x[0][0], x[0][1], x[0][2]))
    return [words for _, words in sorted_lines]


def group_by_blocks(results: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Group OCR results by block (text region)
    
    Args:
        results: Parsed OCR results
        
    Returns:
        Dictionary mapping block number to results
    """
    blocks = {}
    
    for result in results:
        block_num = result["block"]
        if block_num not in blocks:
            blocks[block_num] = []
        blocks[block_num].append(result)
    
    return blocks


def calculate_page_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for the OCR results
    
    Args:
        results: Parsed OCR results
        
    Returns:
        Statistics dictionary
    """
    if not results:
        return {
            "total_words": 0,
            "avg_confidence": 0,
            "min_confidence": 0,
            "max_confidence": 0,
            "total_blocks": 0,
            "total_lines": 0
        }
    
    confidences = [r["confidence"] for r in results if r["confidence"] >= 0]
    blocks = set(r["block"] for r in results)
    lines = set((r["block"], r["paragraph"], r["line"]) for r in results)
    
    return {
        "total_words": len(results),
        "avg_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0,
        "min_confidence": min(confidences) if confidences else 0,
        "max_confidence": max(confidences) if confidences else 0,
        "total_blocks": len(blocks),
        "total_lines": len(lines)
    }
