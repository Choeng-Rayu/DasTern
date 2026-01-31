"""
Enhanced OCR Extraction for Medical Prescriptions
Combines advanced preprocessing, table detection, and structured data extraction
"""
import numpy as np
from typing import Dict, List, Any, Optional
from ..preprocess.advanced import preprocess_for_medical_ocr
from ..engines.tesseract import run_ocr
from ..parsers.tesseract_parser import parse_ocr_data, calculate_page_stats
from .table_extractor import extract_table_structure, detect_tables_in_image
from .structured_data import extract_structured_data
from ...core.config import settings
from ...core.logger import logger


def extract_medical_prescription(
    image: np.ndarray,
    apply_advanced_preprocessing: bool = True,
    detect_tables: bool = True,
    extract_structured: bool = True,
    languages: Optional[str] = None,
    upscale_factor: float = 1.5
) -> Dict[str, Any]:
    """
    Complete medical prescription extraction pipeline
    
    This is the main extraction function that:
    1. Applies advanced preprocessing for medical images
    2. Detects and extracts table structures
    3. Runs enhanced OCR
    4. Extracts structured data (medications, patient info, etc.)
    
    Args:
        image: Input image (BGR format)
        apply_advanced_preprocessing: Use advanced preprocessing
        detect_tables: Detect and extract table structures
        extract_structured: Extract structured data
        languages: OCR languages (default: khm+eng+fra)
        upscale_factor: Image upscaling factor
        
    Returns:
        Comprehensive extraction results
    """
    logger.info("=" * 70)
    logger.info("Starting Medical Prescription OCR Extraction")
    logger.info("=" * 70)
    
    lang = languages or settings.OCR_LANGUAGES
    
    # Step 1: Advanced Preprocessing
    if apply_advanced_preprocessing:
        logger.info("Step 1: Applying advanced preprocessing...")
        processed_image = preprocess_for_medical_ocr(
            image,
            remove_shadow=True,
            deskew=True,
            enhance_contrast=True,
            denoise=True,
            upscale=True,
            upscale_factor=upscale_factor
        )
    else:
        logger.info("Step 1: Skipping advanced preprocessing")
        processed_image = image
    
    # Step 2: Table Detection (if enabled)
    table_data = None
    if detect_tables:
        logger.info("Step 2: Detecting tables...")
        try:
            table_regions = detect_tables_in_image(processed_image)
            
            if table_regions:
                logger.info(f"Found {len(table_regions)} table region(s)")
                
                # Extract the largest table
                largest_table = max(table_regions, key=lambda t: t['area'])
                bbox = largest_table['bbox']
                
                # Extract table region
                table_img = processed_image[
                    bbox['y']:bbox['y']+bbox['h'],
                    bbox['x']:bbox['x']+bbox['w']
                ]
                
                # Extract table structure
                table_data = extract_table_structure(table_img, lang)
                logger.info(f"Extracted table: {table_data.get('rows', 0)} rows x "
                           f"{table_data.get('columns', 0)} columns")
            else:
                logger.info("No tables detected")
        except Exception as e:
            logger.error(f"Table detection failed: {e}")
            table_data = None
    else:
        logger.info("Step 2: Table detection disabled")
    
    # Step 3: Run Enhanced OCR
    logger.info("Step 3: Running enhanced OCR...")
    ocr_data = run_ocr(processed_image, languages=lang)
    
    # Step 4: Parse OCR Results
    logger.info("Step 4: Parsing OCR results...")
    parsed_results = parse_ocr_data(ocr_data, include_low_confidence=True)
    
    # Calculate stats
    stats = calculate_page_stats(parsed_results)
    
    # Step 5: Extract Structured Data (if enabled)
    structured_data = None
    if extract_structured:
        logger.info("Step 5: Extracting structured data...")
        try:
            # Combine all text
            full_text = ' '.join([r['text'] for r in parsed_results if r.get('text')])
            
            structured_data = extract_structured_data(full_text, parsed_results, table_data)
            
            logger.info(f"Structured data extracted: "
                       f"{len(structured_data.get('medications', []))} medications, "
                       f"{len(structured_data.get('dates', []))} dates")
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            structured_data = None
    else:
        logger.info("Step 5: Structured data extraction disabled")
    
    # Compile results
    results = {
        "success": True,
        "page": 1,
        "raw": parsed_results,
        "stats": stats,
        "languages_used": lang,
        "preprocessing_applied": apply_advanced_preprocessing,
        "table_detection": {
            "enabled": detect_tables,
            "found": table_data is not None,
            "data": table_data
        },
        "structured_data": structured_data
    }
    
    logger.info("=" * 70)
    logger.info("Medical Prescription OCR Extraction Complete")
    logger.info(f"Extracted {len(parsed_results)} text elements")
    logger.info(f"Average confidence: {stats.get('avg_confidence', 0):.1f}%")
    logger.info("=" * 70)
    
    return results


def extract_with_multiple_methods(
    image: np.ndarray,
    languages: Optional[str] = None
) -> Dict[str, Any]:
    """
    Try multiple extraction methods and combine results
    Useful for difficult images
    
    Args:
        image: Input image
        languages: OCR languages
        
    Returns:
        Combined results from multiple methods
    """
    logger.info("Running multi-method extraction")
    
    methods = [
        {
            "name": "Advanced (Upscale 2x)",
            "params": {
                "apply_advanced_preprocessing": True,
                "upscale_factor": 2.0
            }
        },
        {
            "name": "Advanced (Upscale 1.5x)",
            "params": {
                "apply_advanced_preprocessing": True,
                "upscale_factor": 1.5
            }
        },
        {
            "name": "Standard",
            "params": {
                "apply_advanced_preprocessing": False
            }
        }
    ]
    
    results = []
    best_result = None
    best_confidence = 0
    
    for method in methods:
        logger.info(f"Trying method: {method['name']}")
        try:
            result = extract_medical_prescription(
                image,
                languages=languages,
                **method['params']
            )
            
            avg_conf = result.get('stats', {}).get('avg_confidence', 0)
            results.append({
                "method": method['name'],
                "result": result,
                "avg_confidence": avg_conf
            })
            
            if avg_conf > best_confidence:
                best_confidence = avg_conf
                best_result = result
        
        except Exception as e:
            logger.error(f"Method {method['name']} failed: {e}")
            continue
    
    logger.info(f"Best method had confidence: {best_confidence:.1f}%")
    
    return {
        "best_result": best_result,
        "all_results": results,
        "best_confidence": best_confidence
    }
