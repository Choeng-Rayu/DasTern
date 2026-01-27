"""
Simple OCR Engine using Tesseract with PaddleOCR-like interface
"""

import cv2
import numpy as np
import pytesseract
from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class PaddleOCRMock:
    """Mock PaddleOCR class that uses Tesseract but provides PaddleOCR-like interface"""
    
    def __init__(self, use_angle_cls=True, lang='en', use_gpu=False):
        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self.use_gpu = use_gpu
        logger.info(f"Initialized PaddleOCR Mock with lang={lang}")
    
    def ocr(self, img_path: str, cls=True) -> List[List[Any]]:
        """
        OCR function that mimics PaddleOCR output format
        Returns: [[[bbox], (text, confidence)], ...]
        """
        try:
            # Read image
            if isinstance(img_path, str):
                image = cv2.imread(img_path)
            else:
                image = img_path
            
            if image is None:
                logger.error(f"Could not read image: {img_path}")
                return []
            
            # Convert to RGB for Tesseract
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get OCR data with bounding boxes
            data = pytesseract.image_to_data(rgb_image, output_type=pytesseract.Output.DICT)
            
            results = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                if int(data['conf'][i]) > 30:  # Filter low confidence
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    text = data['text'][i].strip()
                    
                    if text:  # Only include non-empty text
                        # Create bbox in PaddleOCR format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                        bbox = [
                            [x, y],
                            [x + w, y], 
                            [x + w, y + h],
                            [x, y + h]
                        ]
                        
                        # Confidence as float between 0 and 1
                        confidence = float(data['conf'][i]) / 100.0
                        
                        results.append([bbox, (text, confidence)])
            
            logger.info(f"OCR extracted {len(results)} text blocks")
            return results
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return []

# Global OCR instance
ocr_engine = None

def get_ocr_engine():
    """Get or create OCR engine instance"""
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = PaddleOCRMock(use_angle_cls=True, lang='en')
    return ocr_engine

def extract_text_blocks(image_path: str) -> List[dict]:
    """
    Extract text blocks from image using OCR
    Returns list of text blocks with bounding boxes and confidence
    """
    try:
        ocr = get_ocr_engine()
        results = ocr.ocr(image_path, cls=True)
        
        blocks = []
        for result in results:
            if result and len(result) == 2:
                bbox, (text, confidence) = result
                
                # Convert bbox to simple format
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                
                block = {
                    'text': text,
                    'confidence': confidence,
                    'bbox': {
                        'x1': int(x1),
                        'y1': int(y1), 
                        'x2': int(x2),
                        'y2': int(y2)
                    }
                }
                blocks.append(block)
        
        return blocks
        
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        return []
