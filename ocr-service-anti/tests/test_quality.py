"""Tests for Layer 2: Quality Analysis."""

import pytest
import numpy as np
from PIL import Image
import io

from app.quality.analyzer import QualityAnalyzer
from dataclasses import dataclass


@dataclass
class MockContext:
    """Mock pipeline context for testing."""
    cv_image: np.ndarray
    pil_image: any = None
    quality_metrics: dict = None


class TestQualityAnalyzer:
    """Tests for QualityAnalyzer."""
    
    def setup_method(self):
        self.analyzer = QualityAnalyzer()
    
    def test_analyze_sharp_image(self):
        """Test analysis of a sharp, high-contrast image."""
        # Create a sharp image with good contrast
        img = np.zeros((500, 500), dtype=np.uint8)
        img[100:400, 100:400] = 255  # White rectangle on black
        
        context = MockContext(cv_image=img)
        result = self.analyzer.analyze(context)
        
        assert result.quality_metrics is not None
        assert result.quality_metrics["blur"] in ["low", "medium"]
        assert result.quality_metrics["contrast"] in ["ok", "high"]
    
    def test_analyze_blurry_image(self):
        """Test analysis of a blurry image."""
        # Create and blur an image
        img = np.zeros((500, 500), dtype=np.uint8)
        img[100:400, 100:400] = 255
        
        import cv2
        blurred = cv2.GaussianBlur(img, (51, 51), 0)
        
        context = MockContext(cv_image=blurred)
        result = self.analyzer.analyze(context)
        
        assert result.quality_metrics["blur"] in ["medium", "high"]
    
    def test_skew_detection(self):
        """Test skew angle detection."""
        # Create an image with lines
        img = np.ones((500, 500), dtype=np.uint8) * 255
        import cv2
        cv2.line(img, (50, 100), (450, 120), 0, 2)  # Slightly skewed line
        
        context = MockContext(cv_image=img)
        result = self.analyzer.analyze(context)
        
        # Should detect some skew
        assert "skew_angle" in result.quality_metrics
