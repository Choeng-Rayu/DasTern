"""
Ollama-based AI Service for OCR Correction and Medical Assistance
"""
import os
import sys
import logging
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional

try:
    from .schemas import OCRCorrectionRequest, OCRCorrectionResponse
    from .schemas import ChatRequest, ChatResponse
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from app.schemas import OCRCorrectionRequest, OCRCorrectionResponse
    from app.schemas import ChatRequest, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Ollama AI Service...")
    logger.info(f"Ollama endpoint: {OLLAMA_BASE_URL}")
    logger.info(f"Default model: {DEFAULT_MODEL}")
    
    # Test Ollama connection
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            logger.info(f"Available Ollama models: {model_names}")
            
            if DEFAULT_MODEL not in model_names:
                logger.warning(f"Default model {DEFAULT_MODEL} not found. Available: {model_names}")
        else:
            logger.error(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}")
            raise ConnectionError("Ollama not accessible")
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise
    
    yield
    logger.info("Shutting down Ollama AI Service...")

# Initialize FastAPI
app = FastAPI(
    title="Ollama AI Service",
    description="Ollama-based OCR correction and medical chatbot assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def call_ollama(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.7) -> str:
    """Make a call to Ollama API"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "max_tokens": 512
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"Ollama API error: {response.text}")
    
    except requests.exceptions.Timeout:
        logger.error("Ollama request timeout")
        raise HTTPException(status_code=500, detail="Ollama request timeout")
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Ollama AI Service",
        "status": "running",
        "model": DEFAULT_MODEL,
        "ollama_url": OLLAMA_BASE_URL,
        "capabilities": ["ocr_correction", "chatbot"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "service": "ollama-ai-service", "ollama_connected": True}
        else:
            return {"status": "unhealthy", "service": "ollama-ai-service", "ollama_connected": False}
    except:
        return {"status": "unhealthy", "service": "ollama-ai-service", "ollama_connected": False}

@app.post("/correct-ocr")
async def correct_ocr_simple(request: dict):
    """
    Simple OCR correction endpoint using Ollama
    
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
        
        logger.info(f"Correcting OCR text with Ollama (length: {len(text)})")
        
        # Create OCR correction prompt
        prompt = f"""You are an expert OCR text corrector specializing in medical prescriptions and documents. Please correct the following text, fixing OCR errors while preserving the original meaning.

Language: {language}
Text to correct: {text}

Corrected text:"""

        corrected_text = await call_ollama(prompt, temperature=0.3)  # Lower temperature for more deterministic correction
        
        return {
            "corrected_text": corrected_text,
            "confidence": 0.85,  # Ollama doesn't provide confidence scores
            "corrections_made": 1 if corrected_text != text else 0,
            "model_used": DEFAULT_MODEL
        }
        
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e)
        logger.error(f"Error in OCR correction: {error_msg}", exc_info=True)
        return {
            "corrected_text": request.get("text", ""),
            "confidence": 0.0,
            "corrections_made": 0,
            "error": error_msg
        }

@app.post("/api/v1/correct", response_model=OCRCorrectionResponse)
async def correct_ocr(request: OCRCorrectionRequest):
    """
    Correct OCR text using Ollama
    
    Args:
        request: OCR correction request with raw text
        
    Returns:
        Corrected text with confidence score
    """
    try:
        logger.info(f"Received OCR correction request for language: {request.language}")
        
        result = await correct_ocr_simple({
            "text": request.raw_text,
            "language": request.language
        })
        
        return OCRCorrectionResponse(
            corrected_text=result["corrected_text"],
            confidence=result["confidence"],
            language=request.language,
            corrections_made=result["corrections_made"],
            metadata={"model": DEFAULT_MODEL, "service": "ollama-ai-service"}
        )
        
    except Exception as e:
        logger.error(f"Error in OCR correction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with medical assistant using Ollama
    
    Args:
        request: Chat request with message
        
    Returns:
        AI assistant response
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Create medical assistant prompt
        prompt = f"""You are a helpful medical assistant specializing in prescription reminders and health advice. Based on the user's message, provide clear, helpful, and safe medical information. Always advise consulting a healthcare professional for serious medical concerns.

User message: {request.message}

Response:"""

        response_text = await call_ollama(prompt)
        
        return ChatResponse(
            response=response_text,
            language=request.language,
            metadata={"model": DEFAULT_MODEL, "service": "ollama-ai-service"}
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)