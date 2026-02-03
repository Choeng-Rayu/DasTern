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
    from .schemas import ReminderRequest, ReminderResponse
    from .features.reminder_engine import ReminderEngine
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from app.schemas import OCRCorrectionRequest, OCRCorrectionResponse
    from app.schemas import ChatRequest, ChatResponse
    from app.schemas import ReminderRequest, ReminderResponse
    from app.features.reminder_engine import ReminderEngine

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

# Import async Ollama client
try:
    from .core.ollama_client import OllamaClient
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from app.core.ollama_client import OllamaClient

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
ollama_client = OllamaClient()
reminder_engine = ReminderEngine(ollama_client)

# Initialize prescription processor
try:
    from .features.prescription.processor import PrescriptionProcessor
    prescription_processor = PrescriptionProcessor(ollama_client)
except ImportError:
    # Fallback import logic
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from app.features.prescription.processor import PrescriptionProcessor
    prescription_processor = PrescriptionProcessor(ollama_client)

async def call_ollama(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.7) -> str:
    """Make a call to Ollama API with fallback"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "max_tokens": 100,
                "num_ctx": 512
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30  # Reduced timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"Ollama API error: {response.text}")
    
    except requests.exceptions.Timeout:
        logger.error("Ollama request timeout - using fallback")
        # Use simple fallback for timeout
        return await simple_fallback(prompt)
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return await simple_fallback(prompt)

async def simple_fallback(prompt: str) -> str:
    """Simple fallback when Ollama is too slow"""
    try:
        # Import the fallback function
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from simple_ai_fallback import simple_ocr_correction
        
        # Extract text from prompt (everything after "Fix OCR errors" or similar)
        text_to_fix = prompt
        if "Fix OCR errors" in prompt:
            text_to_fix = prompt.split("Fix OCR errors")[-1].strip()
        if "Fix this text:" in prompt:
            text_to_fix = prompt.split("Fix this text:")[-1].strip()
        
        # Remove common prefixes
        text_to_fix = text_to_fix.replace("in this medical prescription text:", "")
        text_to_fix = text_to_fix.replace("and summarize medical text:", "")
        
        # Clean and use simple correction
        if text_to_fix.startswith('"') and text_to_fix.endswith('"'):
            text_to_fix = text_to_fix[1:-1]
        
        # Handle case where text starts with "Fix: " or similar
        if text_to_fix.startswith("Fix: "):
            text_to_fix = text_to_fix[5:]
            
        result = simple_ocr_correction(text_to_fix.strip())
        
        # For simple fixes like "helo wrold", return just the correction
        if len(result["corrected_text"]) < 50:
            return result["corrected_text"]
        else:
            return result["corrected_text"]
        
    except Exception as e:
        logger.error(f"Fallback failed: {e}")
        return "Text correction temporarily unavailable. Please check back later."

@app.post("/extract-reminders")
def extract_reminders(request: ReminderRequest):
    """Extract structured reminders from raw OCR data"""
    try:
        result = reminder_engine.extract_reminders(request)
        return result
    except Exception as e:
        logger.error(f"Reminder extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/prescription/process")
async def process_prescription(request: ReminderRequest):
    """
    Process full prescription (Patient, Medical, Medications) from raw OCR data.
    """
    try:
        # Use PrescriptionProcessor to get full structured data
        result = prescription_processor.process_prescription(request.raw_ocr_json)
        
        if not result.get("success", False):
            # If processor failed explicitly (but no exception raised)
            return {
                "success": False,
                "error": result.get("error", "Unknown processing error"),
                "patient_info": {},
                "medical_info": {},
                "medications": []
            }
            
        return result
        
    except Exception as e:
        logger.error(f"Prescription processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Ollama AI Service",
        "status": "running",
        "model": DEFAULT_MODEL,
        "ollama_url": OLLAMA_BASE_URL,
        "capabilities": ["ocr_correction", "chatbot", "structured_reminders"]
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
        
        if not text or not text.strip():
            logger.warning(f"Empty text received in OCR correction request: {request}")
            raise HTTPException(status_code=400, detail="No text provided or text is empty. Please ensure the OCR extracted text before sending for correction.")
        
        logger.info(f"Correcting OCR text with Ollama (length: {len(text)})")
        
        # Truncate text if too long for faster processing
        if len(text) > 200:
            text = text[:200] + "..."
            
        # Create simple OCR correction prompt
        prompt = f"Fix OCR errors in this medical prescription text: {text}\n\nCorrected:"

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
        
        # Truncate message if too long for faster processing
        message = request.message
        if len(message) > 200:
            message = message[:200] + "..."
        
        # Create simple prompt for faster processing
        prompt = f"Fix OCR errors and summarize medical text: {message}\n\nCorrected:"

        response_text = await call_ollama(prompt)
        
        return ChatResponse(
            response=response_text,
            language=request.language,
            confidence=0.85,  # Default confidence since Ollama doesn't provide it
            metadata={"model": DEFAULT_MODEL, "service": "ollama-ai-service"}
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)