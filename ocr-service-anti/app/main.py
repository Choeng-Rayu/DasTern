"""
OCR Service - FastAPI Application
A layer-by-layer OCR service for scanning complex Cambodian prescriptions.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.training_routes import router as training_router
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="OCR Service",
    description="A layer-by-layer OCR service for scanning complex prescriptions with mixed Khmer/English/French text",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(training_router, prefix="/api/v1/training")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "OCR Service",
        "version": "1.0.0",
        "description": "Layer-by-layer OCR for Cambodian prescriptions",
        "docs": "/docs",
    }
