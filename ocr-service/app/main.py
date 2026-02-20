"""
OCR Service - Main Application
Tesseract-based multilingual OCR service
Supports: Khmer (khm), English (eng), French (fra)
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logger import logger
from .api.ocr import router as ocr_router
from .ocr.engines.tesseract import check_tesseract_installed, get_available_languages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    if check_tesseract_installed():
        langs = get_available_languages()
        logger.info(f"Tesseract languages available: {langs}")
        required = ["eng", "fra", "khm"]
        missing = [l for l in required if l not in langs]
        if missing:
            logger.warning(f"Missing language packs: {missing}")
    else:
        logger.error("Tesseract not found! OCR will not work.")
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    logger.info("Shutting down OCR Service")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Tesseract-based multilingual OCR for Khmer/English/French prescriptions",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": f"{settings.API_V1_PREFIX}/ocr"
    }


@app.get("/health")
async def health():
    tesseract_ok = check_tesseract_installed()
    return {
        "status": "healthy" if tesseract_ok else "degraded",
        "tesseract": tesseract_ok
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
