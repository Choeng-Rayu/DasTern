"""
AI LLM Service - MT5 Model API
Handles OCR correction and chatbot functionality
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from .schemas import OCRCorrectionRequest, OCRCorrectionResponse
    from .schemas import ChatRequest, ChatResponse
    from .ocr_corrector import correct_ocr_text
    from .chat_assistant import chat_with_assistant
    from .model_loader import load_mt5_model
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from app.schemas import OCRCorrectionRequest, OCRCorrectionResponse
    from app.schemas import ChatRequest, ChatResponse
    from app.ocr_corrector import correct_ocr_text
    from app.chat_assistant import chat_with_assistant
    from app.model_loader import load_mt5_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading MT5 model...")
    load_mt5_model()
    logger.info("MT5 model loaded successfully!")
    yield

# Initialize FastAPI
app = FastAPI(
    title="AI LLM Service",
    description="MT5-based OCR correction and medical chatbot assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AI LLM Service",
        "status": "running",
        "model": "MT5-small",
        "capabilities": ["ocr_correction", "chatbot"]
    }

@app.post("/api/v1/correct", response_model=OCRCorrectionResponse)
async def correct_ocr(request: OCRCorrectionRequest):
    """
    Correct OCR text using MT5 model
    
    Args:
        request: OCR correction request with raw text
        
    Returns:
        Corrected text with confidence score
    """
    try:
        logger.info(f"Received OCR correction request for language: {request.language}")
        
        result = correct_ocr_text(
            raw_text=request.raw_text,
            language=request.language,
            context=request.context
        )
        
        return OCRCorrectionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in OCR correction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/correct-ocr")
async def correct_ocr_simple(request: dict):
    """
    Simple OCR correction endpoint for backend integration
    
    Args:
        request: Dict with 'text' and optional 'language'
        
    Returns:
        Dict with corrected_text and confidence
    """
    try:
        text = request.get("text", "")
        language = request.get("language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        logger.info(f"Correcting OCR text (length: {len(text)})")
        
        result = correct_ocr_text(
            raw_text=text,
            language=language,
            context=None
        )
        
        return {
            "corrected_text": result.get("corrected_text", text),
            "confidence": result.get("confidence", 0.0),
            "corrections_made": result.get("corrections_made", 0)
        }
        
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e)
        logger.error(f"Error in OCR correction: {error_msg}", exc_info=True)
        # Return original text if correction fails
        return {
            "corrected_text": request.get("text", ""),
            "confidence": 0.5,
            "corrections_made": 0,
            "error": error_msg
        }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with medical assistant
    
    Args:
        request: Chat request with message
        
    Returns:
        AI assistant response
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        result = chat_with_assistant(
            message=request.message,
            language=request.language,
            context=request.context
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-llm-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
