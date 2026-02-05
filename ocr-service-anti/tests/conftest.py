"""Test configuration and fixtures."""

import pytest
import io
from pathlib import Path
from PIL import Image
import numpy as np


@pytest.fixture
def sample_image_bytes():
    """Create a simple test image."""
    img = Image.new('RGB', (800, 600), color='white')
    # Draw some text-like content
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 700, 500], outline='black')
    draw.text((150, 150), "Sample Text", fill='black')
    draw.text((150, 200), "ព្រឹក ល្ org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org org ច", fill='black')
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.fixture
def sample_image_path(tmp_path, sample_image_bytes):
    """Save sample image to temp path."""
    img_path = tmp_path / "test_image.png"
    with open(img_path, 'wb') as f:
        f.write(sample_image_bytes)
    return img_path


@pytest.fixture
def corrupted_image_bytes():
    """Create corrupted image bytes."""
    return b"not a valid image"


@pytest.fixture
def small_image_bytes():
    """Create a very small image."""
    img = Image.new('RGB', (50, 50), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
