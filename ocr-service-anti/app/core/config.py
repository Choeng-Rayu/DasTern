"""
Configuration settings for the OCR Service.
Uses Pydantic Settings for environment variable management.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # General
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Server Configuration
    ocr_service_host: str = Field(default="0.0.0.0", description="OCR service host")
    ocr_service_port: int = Field(default=8000, description="OCR service port")
    
    # External Service URLs
    ai_llm_service_url: str = Field(
        default="http://localhost:8001",
        description="AI-LLM service URL"
    )
    
    # Tesseract Configuration
    tesseract_cmd: str = Field(
        default="/usr/bin/tesseract",
        description="Path to Tesseract executable"
    )
    default_languages: str = Field(
        default="eng+khm+fra",
        description="Default OCR languages"
    )
    
    # DPI Settings
    min_dpi: int = Field(default=150, description="Minimum acceptable DPI")
    preferred_dpi: int = Field(default=300, description="Preferred DPI for OCR")
    
    # Quality Thresholds
    blur_threshold_low: float = Field(
        default=100.0,
        description="Laplacian variance below this is considered blurry"
    )
    blur_threshold_high: float = Field(
        default=50.0,
        description="Laplacian variance below this is very blurry"
    )
    contrast_threshold_low: float = Field(
        default=30.0,
        description="Standard deviation below this is low contrast"
    )
    contrast_threshold_high: float = Field(
        default=200.0,
        description="Standard deviation above this is high contrast"
    )
    
    # Image Constraints
    min_image_width: int = Field(default=100, description="Minimum image width in pixels")
    min_image_height: int = Field(default=100, description="Minimum image height in pixels")
    max_image_size_mb: float = Field(default=50.0, description="Maximum image size in MB")
    supported_formats: List[str] = Field(
        default=["jpg", "jpeg", "png", "webp", "tiff", "bmp"],
        description="Supported image formats"
    )
    
    # Model Settings
    custom_model_path: Path = Field(
        default=Path("./training_data/models"),
        description="Path to custom trained models"
    )
    active_model: str = Field(
        default="default",
        description="Currently active model name"
    )
    
    # Preprocessing Settings
    max_skew_angle: float = Field(
        default=45.0,
        description="Maximum skew angle to correct"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_tesseract_languages() -> List[str]:
    """Get list of configured languages."""
    return settings.default_languages.split("+")


def get_tessdata_path() -> Optional[str]:
    """Get tessdata path if custom models are used."""
    if settings.active_model != "default":
        model_path = settings.custom_model_path / settings.active_model
        if model_path.exists():
            return str(model_path)
    return None
