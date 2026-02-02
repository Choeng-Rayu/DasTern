"""Tests for the complete OCR Pipeline."""

import pytest
from unittest.mock import MagicMock, patch
import numpy as np


class TestOCRPipeline:
    """Integration tests for the OCR pipeline."""
    
    @pytest.mark.asyncio
    async def test_pipeline_processes_valid_image(self, sample_image_bytes):
        """Test that pipeline processes a valid image."""
        # This test requires Tesseract to be installed
        pytest.importorskip("pytesseract")
        
        from app.core.pipeline import OCRPipeline
        
        pipeline = OCRPipeline()
        
        try:
            result = await pipeline.process(
                image_bytes=sample_image_bytes,
                filename="test.png"
            )
            
            assert result is not None
            assert result.meta is not None
            assert result.quality is not None
            assert isinstance(result.blocks, list)
        except Exception as e:
            # May fail if Tesseract not installed
            if "Tesseract" in str(e):
                pytest.skip("Tesseract not installed")
            raise
    
    @pytest.mark.asyncio
    async def test_quality_only_analysis(self, sample_image_bytes):
        """Test quality-only analysis mode."""
        from app.core.pipeline import OCRPipeline
        
        pipeline = OCRPipeline()
        
        result = await pipeline.analyze_quality_only(
            image_bytes=sample_image_bytes,
            filename="test.png"
        )
        
        assert result is not None
        assert hasattr(result, 'blur')
        assert hasattr(result, 'contrast')
