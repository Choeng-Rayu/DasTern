"""
OCR Service - Main Application
Tesseract-based multilingual OCR service
Supports: Khmer (khm), English (eng), French (fra)
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logger import logger
from .api.ocr import router as ocr_router
from .ocr.engines.tesseract import check_tesseract_installed, get_available_languages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Check Tesseract
    if check_tesseract_installed():
        langs = get_available_languages()
        logger.info(f"Tesseract languages available: {langs}")
        
        # Check for required languages
        required = ["eng", "fra", "khm"]
        missing = [l for l in required if l not in langs]
        if missing:
            logger.warning(f"Missing language packs: {missing}")
            logger.warning("Install with: sudo apt install tesseract-ocr-khm tesseract-ocr-fra tesseract-ocr-eng")
    else:
        logger.error("Tesseract not found! OCR will not work.")
    
    # Create directories
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Results directory: {settings.RESULTS_DIR.absolute()}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OCR Service")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## OCR Service (Tesseract)
    
    Extract raw text from images using Tesseract OCR.
    
    ### Features:
    - **Multilingual OCR**: Khmer (khm) + English (eng) + French (fra)
    - **Bounding Boxes**: Position of each detected text element
    - **Confidence Scores**: Accuracy confidence for each element
    - **Structure Metadata**: Block, line, and word information
    
    ### Important:
    This service provides **RAW OCR output only**.
    - NO interpretation
    - NO fixing
    - NO guessing
    - NO translation
    
    Use the AI/LLM service for text interpretation and correction.
    """,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - service info"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": f"{settings.API_V1_PREFIX}/ocr"
    }


@app.get("/health")
async def health():
    """Simple health check"""
    tesseract_ok = check_tesseract_installed()
    return {
        "status": "healthy" if tesseract_ok else "degraded",
        "tesseract": tesseract_ok
    }


# Entry point for running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
