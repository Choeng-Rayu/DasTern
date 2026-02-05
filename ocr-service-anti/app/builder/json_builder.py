"""
Layer 7: Raw OCR JSON Builder

Purpose: Build the final structured JSON output
- Preserves all bounding boxes
- Includes confidence scores
- Maintains block/line/word structure
- Adds semantic tags (without filtering)
- AI-ready format

This is what gets sent to the AI for enhancement.
"""

from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.responses import (
    OCRResponse,
    ProcessingMeta,
    QualityMetrics,
    Block,
    TextLine,
    BoundingBox,
    BlockType,
    BlurLevel,
    ContrastLevel,
    QRCodeData,
    TableBlock,
    TableCell,
)
from app.postprocess.cleaner import TextCleaner
from app.layout.detector import LayoutBlock

logger = get_logger(__name__)


class JSONBuilder:
    """
    Builds the final OCR JSON response.
    
    Combines results from all layers into a structured,
    AI-friendly JSON format with bounding boxes preserved.
    """
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
    
    def build(self, context) -> OCRResponse:
        """
        Build the final OCR response from pipeline context.
        
        Args:
            context: PipelineContext with all layer outputs
        
        Returns:
            OCRResponse with complete structured data
        """
        logger.info("Building OCR JSON response")
        
        # Build metadata
        meta = self._build_meta(context)
        
        # Build quality metrics
        quality = self._build_quality(context)
        
        # Build QR code data
        qr_codes = self._build_qr_codes(context)
        
        # Build blocks with OCR results
        blocks = self._build_blocks(context)
        
        # Build raw text (concatenated, reading order)
        raw_text = self._build_raw_text(blocks)
        
        response = OCRResponse(
            meta=meta,
            quality=quality,
            qr_codes=qr_codes,
            blocks=blocks,
            raw_text=raw_text
        )
        
        logger.info(
            f"Built response: {len(blocks)} blocks, "
            f"{sum(len(b.lines) for b in blocks)} lines"
        )
        
        return response
    
    def _build_meta(self, context) -> ProcessingMeta:
        """Build processing metadata."""
        # Get languages used
        languages = settings.default_languages.split('+')
        
        # Get image size
        image_size = {}
        if context.pil_image:
            image_size = {
                "width": context.pil_image.size[0],
                "height": context.pil_image.size[1]
            }
        elif context.cv_image is not None:
            h, w = context.cv_image.shape[:2]
            image_size = {"width": w, "height": h}
        
        # Get DPI
        dpi = None
        if context.quality_metrics:
            dpi = context.quality_metrics.get("dpi")
        
        return ProcessingMeta(
            languages=languages,
            dpi=dpi,
            processing_time_ms=context.total_time_ms,
            model_version=settings.active_model,
            stage_times=context.stage_times,
            image_size=image_size
        )
    
    def _build_quality(self, context) -> QualityMetrics:
        """Build quality metrics from analysis."""
        qm = context.quality_metrics or {}
        
        # Map string to enum
        blur_map = {"low": BlurLevel.LOW, "medium": BlurLevel.MEDIUM, "high": BlurLevel.HIGH}
        contrast_map = {"low": ContrastLevel.LOW, "ok": ContrastLevel.OK, "high": ContrastLevel.HIGH}
        
        return QualityMetrics(
            blur=blur_map.get(qm.get("blur", "low"), BlurLevel.LOW),
            blur_score=qm.get("blur_score", 0.0),
            contrast=contrast_map.get(qm.get("contrast", "ok"), ContrastLevel.OK),
            contrast_score=qm.get("contrast_score", 0.0),
            skew_angle=qm.get("skew_angle", 0.0),
            dpi=qm.get("dpi"),
            is_grayscale=qm.get("is_grayscale", False)
        )
    
    def _build_qr_codes(self, context) -> List[QRCodeData]:
        """Extract QR code data from layout blocks."""
        qr_codes = []
        
        for block in context.layout_blocks or []:
            if block.type == BlockType.QR_CODE:
                qr_data = getattr(block, 'qr_data', None)
                if qr_data:
                    qr_codes.append(QRCodeData(
                        data=qr_data,
                        bbox=BoundingBox(
                            x=block.x,
                            y=block.y,
                            width=block.width,
                            height=block.height
                        ),
                        type="QR"
                    ))
        
        return qr_codes
    
    def _build_blocks(self, context) -> List[Block]:
        """Build blocks from OCR results."""
        blocks = []
        
        # Get cleaned results
        ocr_results = context.cleaned_results or context.ocr_results or []
        
        for i, ocr_block in enumerate(ocr_results):
            # Get corresponding layout block info
            layout_block = None
            if context.layout_blocks and i < len(context.layout_blocks):
                layout_block = context.layout_blocks[i]
            
            # Build text lines
            lines = []
            for line in ocr_block.lines:
                # Add semantic tags
                tags = self.text_cleaner.add_semantic_tags(line.text)
                
                text_line = TextLine(
                    text=line.text,
                    bbox=BoundingBox(
                        x=line.x,
                        y=line.y,
                        width=line.width,
                        height=line.height
                    ),
                    confidence=line.confidence,
                    language=self._detect_line_language(line.text),
                    tags=tags
                )
                lines.append(text_line)
            
            # Determine block type
            block_type = ocr_block.block_type
            if layout_block:
                block_type = layout_block.type
            
            # Build block
            block = Block(
                type=block_type,
                bbox=BoundingBox(
                    x=ocr_block.x,
                    y=ocr_block.y,
                    width=ocr_block.width,
                    height=ocr_block.height
                ),
                lines=lines,
                raw_text="\n".join(line.text for line in lines)
            )
            
            blocks.append(block)
        
        return blocks
    
    def _build_raw_text(self, blocks: List[Block]) -> str:
        """Build concatenated raw text in reading order."""
        text_parts = []
        
        for block in blocks:
            if block.raw_text:
                text_parts.append(block.raw_text)
        
        return "\n\n".join(text_parts)
    
    def _detect_line_language(self, text: str) -> Optional[str]:
        """
        Detect primary language of a line.
        Returns: 'kh', 'en', 'fr', or None
        """
        if not text:
            return None
        
        khmer_count = sum(1 for c in text if 0x1780 <= ord(c) <= 0x17FF)
        latin_count = sum(1 for c in text if c.isalpha() and ord(c) < 256)
        
        total = khmer_count + latin_count
        if total == 0:
            return None
        
        if khmer_count / total > 0.5:
            return "kh"
        
        # Distinguish French from English by accent marks
        french_chars = set('àâäéèêëïîôùûüÿœæç')
        if any(c.lower() in french_chars for c in text):
            return "fr"
        
        return "en"
    
    def build_table_structure(
        self, 
        block: Block, 
        table_info: Dict[str, Any]
    ) -> TableBlock:
        """
        Build table structure with cells.
        """
        rows = table_info.get("rows", 0)
        cols = table_info.get("cols", 0)
        
        # Extract headers (first row)
        headers = []
        if block.lines and rows > 0:
            first_row_lines = [
                l for l in block.lines 
                if l.bbox.y < table_info.get("row_positions", [0, 100])[1]
            ]
            headers = [l.text for l in first_row_lines]
        
        # Build cells by assigning text to grid cells
        cells = []
        row_positions = table_info.get("row_positions", [])
        col_positions = table_info.get("col_positions", [])
        
        for line in block.lines:
            # Find row index
            row_idx = 0
            for i, pos in enumerate(row_positions[:-1]):
                if line.bbox.y >= pos:
                    row_idx = i
            
            # Find col index
            col_idx = 0
            for i, pos in enumerate(col_positions[:-1]):
                if line.bbox.x >= pos:
                    col_idx = i
            
            cells.append(TableCell(
                row=row_idx,
                col=col_idx,
                text=line.text,
                bbox=line.bbox,
                confidence=line.confidence
            ))
        
        return TableBlock(
            rows=rows,
            cols=cols,
            headers=headers,
            cells=cells
        )
