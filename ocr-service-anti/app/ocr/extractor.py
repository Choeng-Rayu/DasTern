"""
Layer 5: OCR Extraction (Tesseract)

Purpose: Extract text from image using Tesseract OCR
- Multi-language support: eng+khm+fra
- Word-level extraction with confidence scores
- Bounding box for each word
- Uses LSTM engine (OEM 1)

Tesseract returns raw truth, not meaning.
"""

import numpy as np
import cv2
import pytesseract
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from app.core.config import settings, get_tessdata_path
from app.core.logging import get_logger
from app.core.exceptions import (
    OCRExtractionError, 
    TesseractNotFoundError,
    LanguageNotAvailableError
)
from app.schemas.responses import BlockType

logger = get_logger(__name__)


@dataclass
class OCRWord:
    """Represents a single recognized word."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    block_num: int = 0
    line_num: int = 0
    word_num: int = 0


@dataclass
class OCRLine:
    """Represents a line of text."""
    text: str
    words: List[OCRWord] = field(default_factory=list)
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    confidence: float = 0.0


@dataclass 
class OCRBlock:
    """Represents a block of OCR results."""
    lines: List[OCRLine] = field(default_factory=list)
    block_type: BlockType = BlockType.TEXT
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


class OCRExtractor:
    """
    Extracts text from images using Tesseract OCR.
    
    Supports multilingual extraction with bounding boxes
    and confidence scores.
    """
    
    def __init__(self):
        self.tesseract_cmd = settings.tesseract_cmd
        self.default_languages = settings.default_languages
        
        # Set Tesseract path
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        # Verify Tesseract is available
        self._verify_tesseract()
    
    def _verify_tesseract(self) -> None:
        """Verify Tesseract is installed and working."""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            raise TesseractNotFoundError(
                message=f"Tesseract not found at {self.tesseract_cmd}: {e}"
            )
    
    def extract(
        self, 
        context, 
        languages: Optional[str] = None
    ) -> 'PipelineContext':
        """
        Extract text from image using Tesseract.
        
        Args:
            context: PipelineContext with preprocessed_image and layout_blocks
            languages: Override languages (e.g., "eng+khm")
        
        Returns:
            Updated context with ocr_results
        """
        logger.info("Extracting text with Tesseract OCR")
        
        # Use preprocessed image or original
        image = context.preprocessed_image
        if image is None:
            image = context.cv_image
        
        # Determine languages
        lang = languages or self.default_languages
        
        # Get custom tessdata path if using trained model
        tessdata_path = get_tessdata_path()
        
        try:
            # Extract from each layout block
            ocr_results = []
            
            if context.layout_blocks:
                for block in context.layout_blocks:
                    if block.type == BlockType.QR_CODE:
                        # Skip QR codes - already decoded in layout
                        continue
                    
                    # Extract region
                    x, y, w, h = block.x, block.y, block.width, block.height
                    block_image = image[y:y+h, x:x+w]
                    
                    # OCR this block
                    block_result = self._ocr_region(
                        block_image, 
                        lang, 
                        tessdata_path,
                        offset=(x, y)
                    )
                    block_result.block_type = block.type
                    block_result.x = x
                    block_result.y = y
                    block_result.width = w
                    block_result.height = h
                    
                    ocr_results.append(block_result)
            else:
                # No layout blocks - OCR whole image
                block_result = self._ocr_region(
                    image, 
                    lang, 
                    tessdata_path,
                    offset=(0, 0)
                )
                ocr_results.append(block_result)
            
            context.ocr_results = ocr_results
            
            total_words = sum(
                len(line.words) 
                for block in ocr_results 
                for line in block.lines
            )
            logger.info(f"Extracted {total_words} words from {len(ocr_results)} blocks")
            
            return context
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise OCRExtractionError(
                message=f"OCR extraction failed: {str(e)}"
            )
    
    def _ocr_region(
        self,
        image: np.ndarray,
        lang: str,
        tessdata_path: Optional[str],
        offset: Tuple[int, int] = (0, 0)
    ) -> OCRBlock:
        """
        Run OCR on a specific image region.
        """
        if image.size == 0:
            return OCRBlock()
        
        # Tesseract config
        config = [
            "--oem 1",  # LSTM engine
            "--psm 6",  # Assume uniform block of text
        ]
        if tessdata_path:
            config.append(f"--tessdata-dir {tessdata_path}")
        
        config_str = " ".join(config)
        
        # Get detailed OCR data
        try:
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                config=config_str,
                output_type=pytesseract.Output.DICT
            )
        except Exception as e:
            if "Failed loading language" in str(e):
                raise LanguageNotAvailableError(
                    message=f"Language not available: {lang}",
                    details={"requested": lang}
                )
            raise
        
        # Parse results into structured format
        offset_x, offset_y = offset
        words_by_line: Dict[Tuple[int, int], List[OCRWord]] = {}
        
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            
            # Skip empty or low-confidence results
            if not text or conf < 0:
                continue
            
            block_num = data['block_num'][i]
            line_num = data['line_num'][i]
            word_num = data['word_num'][i]
            
            word = OCRWord(
                text=text,
                x=data['left'][i] + offset_x,
                y=data['top'][i] + offset_y,
                width=data['width'][i],
                height=data['height'][i],
                confidence=conf / 100.0,
                block_num=block_num,
                line_num=line_num,
                word_num=word_num
            )
            
            key = (block_num, line_num)
            if key not in words_by_line:
                words_by_line[key] = []
            words_by_line[key].append(word)
        
        # Build lines from words
        lines = []
        for key in sorted(words_by_line.keys()):
            words = words_by_line[key]
            if not words:
                continue
            
            # Sort words left to right
            words.sort(key=lambda w: w.x)
            
            # Build line text
            line_text = " ".join(w.text for w in words)
            
            # Calculate line bounding box
            min_x = min(w.x for w in words)
            min_y = min(w.y for w in words)
            max_x = max(w.x + w.width for w in words)
            max_y = max(w.y + w.height for w in words)
            
            # Average confidence
            avg_conf = sum(w.confidence for w in words) / len(words)
            
            lines.append(OCRLine(
                text=line_text,
                words=words,
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y,
                confidence=avg_conf
            ))
        
        # Sort lines top to bottom
        lines.sort(key=lambda l: l.y)
        
        return OCRBlock(lines=lines)
    
    def get_available_languages(self) -> List[str]:
        """Get list of available Tesseract languages."""
        try:
            langs = pytesseract.get_languages()
            return langs
        except Exception:
            return []
    
    def detect_script(self, image: np.ndarray) -> str:
        """
        Detect the primary script in an image.
        Returns: 'Khmer', 'Latin', or 'Mixed'
        """
        try:
            # Use Tesseract OSD (Orientation and Script Detection)
            osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
            script = osd.get('script', 'Latin')
            return script
        except Exception:
            return 'Mixed'
