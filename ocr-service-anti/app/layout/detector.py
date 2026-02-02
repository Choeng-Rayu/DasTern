"""
Layer 4: Layout Analysis

Purpose: Detect document structure WITHOUT understanding meaning
- Detect tables
- Separate columns
- Preserve reading order
- Avoid text mixing
- Detect blocks: Header, Table, Footer, Signature

NO NLP, NO field extraction, NO medical understanding.
Only structural analysis.
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

from app.core.logging import get_logger
from app.core.exceptions import LayoutDetectionError
from app.schemas.responses import BlockType

logger = get_logger(__name__)


@dataclass
class LayoutBlock:
    """Represents a detected layout block."""
    type: BlockType
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    children: List['LayoutBlock'] = field(default_factory=list)
    
    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)
    
    @property
    def area(self) -> int:
        return self.width * self.height


class LayoutDetector:
    """
    Detects document layout structure.
    
    Identifies:
    - Header regions (top of document)
    - Table structures
    - Text blocks
    - Footer regions (bottom of document)
    - Signature areas
    - QR codes
    """
    
    def __init__(self):
        self.min_block_area = 100  # Minimum area for a valid block
        self.header_ratio = 0.15  # Top 15% is potential header
        self.footer_ratio = 0.15  # Bottom 15% is potential footer
    
    def detect(self, context) -> 'PipelineContext':
        """
        Detect layout blocks in the image.
        
        Args:
            context: PipelineContext with preprocessed_image
        
        Returns:
            Updated context with layout_blocks
        """
        logger.info("Detecting layout structure")
        
        try:
            # Use preprocessed or original image
            image = context.preprocessed_image
            if image is None:
                image = context.cv_image
            
            # Get binary image for contour detection
            binary = getattr(context, 'binary_image', None)
            if binary is None:
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                else:
                    gray = image
                _, binary = cv2.threshold(
                    gray, 0, 255, 
                    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
                )
            else:
                # Invert if needed (text should be white on black)
                binary = cv2.bitwise_not(binary)
            
            h, w = binary.shape[:2]
            
            # Detect different types of blocks
            blocks = []
            
            # Detect QR codes first
            qr_blocks = self._detect_qr_codes(context.cv_image)
            blocks.extend(qr_blocks)
            
            # Detect tables
            table_blocks = self._detect_tables(binary, w, h)
            blocks.extend(table_blocks)
            
            # Detect text regions
            text_blocks = self._detect_text_regions(binary, w, h, table_blocks)
            
            # Classify text blocks as header/footer/text
            classified_blocks = self._classify_blocks(text_blocks, h)
            blocks.extend(classified_blocks)
            
            # Sort blocks by reading order (top to bottom, left to right)
            blocks = self._sort_reading_order(blocks)
            
            # Store in context
            context.layout_blocks = blocks
            
            logger.info(f"Detected {len(blocks)} layout blocks")
            
            return context
            
        except Exception as e:
            logger.error(f"Layout detection failed: {e}")
            raise LayoutDetectionError(
                message=f"Layout detection failed: {str(e)}"
            )
    
    def _detect_tables(
        self, 
        binary: np.ndarray, 
        img_width: int, 
        img_height: int
    ) -> List[LayoutBlock]:
        """
        Detect table structures using line detection.
        """
        tables = []
        
        # Detect horizontal lines
        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, 
            (img_width // 10, 1)
        )
        horizontal_lines = cv2.morphologyEx(
            binary, 
            cv2.MORPH_OPEN, 
            horizontal_kernel,
            iterations=2
        )
        
        # Detect vertical lines
        vertical_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, 
            (1, img_height // 10)
        )
        vertical_lines = cv2.morphologyEx(
            binary, 
            cv2.MORPH_OPEN, 
            vertical_kernel,
            iterations=2
        )
        
        # Combine lines
        table_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # Find table regions
        contours, _ = cv2.findContours(
            table_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter by size - tables should be reasonably large
            if area > self.min_block_area * 100 and w > 100 and h > 50:
                tables.append(LayoutBlock(
                    type=BlockType.TABLE,
                    x=x, y=y, width=w, height=h,
                    confidence=0.8
                ))
        
        return tables
    
    def _detect_text_regions(
        self, 
        binary: np.ndarray,
        img_width: int,
        img_height: int,
        exclude_blocks: List[LayoutBlock]
    ) -> List[LayoutBlock]:
        """
        Detect text regions using morphological operations.
        """
        # Create mask of areas to exclude (tables, etc.)
        exclude_mask = np.zeros(binary.shape, dtype=np.uint8)
        for block in exclude_blocks:
            cv2.rectangle(
                exclude_mask,
                (block.x, block.y),
                (block.x + block.width, block.y + block.height),
                255,
                -1
            )
        
        # Remove excluded areas from binary
        text_binary = cv2.bitwise_and(
            binary, 
            cv2.bitwise_not(exclude_mask)
        )
        
        # Dilate to connect text into blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        dilated = cv2.dilate(text_binary, kernel, iterations=3)
        
        # Find text region contours
        contours, _ = cv2.findContours(
            dilated,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        text_blocks = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area > self.min_block_area:
                text_blocks.append(LayoutBlock(
                    type=BlockType.TEXT,
                    x=x, y=y, width=w, height=h,
                    confidence=0.7
                ))
        
        return text_blocks
    
    def _classify_blocks(
        self, 
        blocks: List[LayoutBlock], 
        img_height: int
    ) -> List[LayoutBlock]:
        """
        Classify text blocks as header, footer, or regular text.
        """
        header_threshold = int(img_height * self.header_ratio)
        footer_threshold = int(img_height * (1 - self.footer_ratio))
        
        classified = []
        for block in blocks:
            center_y = block.y + block.height // 2
            
            if center_y < header_threshold:
                block.type = BlockType.HEADER
            elif center_y > footer_threshold:
                # Check if it might be a signature
                if self._looks_like_signature(block):
                    block.type = BlockType.SIGNATURE
                else:
                    block.type = BlockType.FOOTER
            else:
                block.type = BlockType.TEXT
            
            classified.append(block)
        
        return classified
    
    def _looks_like_signature(self, block: LayoutBlock) -> bool:
        """
        Heuristic to detect signature blocks.
        Signatures are typically small, wide, and in the bottom right.
        """
        # TODO: Add more sophisticated signature detection
        aspect_ratio = block.width / max(block.height, 1)
        return aspect_ratio > 2 and block.height < 100
    
    def _detect_qr_codes(self, image: np.ndarray) -> List[LayoutBlock]:
        """
        Detect QR codes in the image.
        """
        qr_blocks = []
        
        try:
            from pyzbar import pyzbar
            
            # Decode QR codes
            decoded = pyzbar.decode(image)
            
            for obj in decoded:
                if obj.type == 'QRCODE':
                    x, y, w, h = obj.rect
                    block = LayoutBlock(
                        type=BlockType.QR_CODE,
                        x=x, y=y, width=w, height=h,
                        confidence=1.0
                    )
                    # Store decoded data
                    block.qr_data = obj.data.decode('utf-8', errors='ignore')
                    qr_blocks.append(block)
                    
        except ImportError:
            logger.warning("pyzbar not available - QR detection disabled")
        except Exception as e:
            logger.warning(f"QR detection failed: {e}")
        
        return qr_blocks
    
    def _sort_reading_order(
        self, 
        blocks: List[LayoutBlock]
    ) -> List[LayoutBlock]:
        """
        Sort blocks in reading order (top to bottom, left to right).
        """
        # Sort by y first, then x
        # Use center of block for comparison
        return sorted(
            blocks,
            key=lambda b: (b.y + b.height // 2, b.x)
        )
    
    def detect_table_structure(
        self, 
        image: np.ndarray, 
        table_block: LayoutBlock
    ) -> Dict[str, Any]:
        """
        Detect internal table structure (rows, columns).
        """
        # Extract table region
        x, y, w, h = table_block.bbox
        table_img = image[y:y+h, x:x+w]
        
        if len(table_img.shape) == 3:
            gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = table_img
        
        _, binary = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        # Detect horizontal lines for rows
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w // 5, 1))
        h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)
        
        # Detect vertical lines for columns
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h // 5))
        v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel)
        
        # Find row positions
        h_proj = np.sum(h_lines, axis=1)
        row_positions = np.where(h_proj > w * 0.3)[0]
        
        # Find column positions
        v_proj = np.sum(v_lines, axis=0)
        col_positions = np.where(v_proj > h * 0.3)[0]
        
        # Cluster positions to get distinct rows/columns
        rows = self._cluster_positions(row_positions)
        cols = self._cluster_positions(col_positions)
        
        return {
            "rows": len(rows) - 1 if rows else 0,
            "cols": len(cols) - 1 if cols else 0,
            "row_positions": rows,
            "col_positions": cols,
        }
    
    def _cluster_positions(
        self, 
        positions: np.ndarray, 
        min_gap: int = 10
    ) -> List[int]:
        """
        Cluster nearby positions into distinct lines.
        """
        if len(positions) == 0:
            return []
        
        clusters = [[positions[0]]]
        for pos in positions[1:]:
            if pos - clusters[-1][-1] <= min_gap:
                clusters[-1].append(pos)
            else:
                clusters.append([pos])
        
        # Return center of each cluster
        return [int(np.mean(c)) for c in clusters]
