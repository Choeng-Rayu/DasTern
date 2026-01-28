"""
OCR Service Configuration
Loads settings from environment variables
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """OCR Service Settings"""
    
    # Service Configuration
    APP_NAME: str = "OCR Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # Tesseract Configuration
    OCR_LANGUAGES: str = "khm+eng+fra"  # Khmer first (dominant in Cambodia)
    OCR_OEM: int = 3  # Default OCR Engine Mode (LSTM + Legacy)
    OCR_PSM: int = 6  # Page segmentation mode (Uniform block of text)
    OCR_CONFIDENCE_THRESHOLD: int = 0  # Minimum confidence (0 = include all)
    
    # User words file path (for custom Khmer words)
    USER_WORDS_PATH: str | None = None
    
    # Image preprocessing
    DENOISE_STRENGTH: int = 15
    ADAPTIVE_THRESHOLD_BLOCK_SIZE: int = 31
    ADAPTIVE_THRESHOLD_C: int = 10
    
    # File storage
    UPLOAD_DIR: Path = Path("uploads")
    RESULTS_DIR: Path = Path("results")
    MAX_FILE_SIZE_MB: int = 10
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
