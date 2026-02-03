"""Tests for Layer 1: Image Intake & Validation."""

import pytest
from app.intake.validator import ImageValidator
from app.core.exceptions import (
    ImageCorruptedError,
    ImageTooSmallError,
)
from dataclasses import dataclass, field


@dataclass
class MockContext:
    """Mock pipeline context for testing."""
    image_bytes: bytes
    filename: str = "test.png"
    pil_image: any = None
    cv_image: any = None


class TestImageValidator:
    """Tests for ImageValidator."""
    
    def setup_method(self):
        self.validator = ImageValidator()
    
    def test_validate_valid_image(self, sample_image_bytes):
        """Test validation of a valid image."""
        context = MockContext(
            image_bytes=sample_image_bytes,
            filename="test.png"
        )
        
        result = self.validator.validate(context)
        
        assert result.pil_image is not None
        assert result.cv_image is not None
    
    def test_validate_corrupted_image(self, corrupted_image_bytes):
        """Test rejection of corrupted image."""
        context = MockContext(
            image_bytes=corrupted_image_bytes,
            filename="corrupted.png"
        )
        
        with pytest.raises(ImageCorruptedError):
            self.validator.validate(context)
    
    def test_validate_small_image(self, small_image_bytes):
        """Test rejection of too-small image."""
        context = MockContext(
            image_bytes=small_image_bytes,
            filename="small.png"
        )
        
        with pytest.raises(ImageTooSmallError):
            self.validator.validate(context)
