"""
AI LLM Service - Ollama-based API
Handles OCR correction and chatbot functionality using Ollama
"""
import os
import sys
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Service...")
    # Note: Using Ollama for inference, no local model loading needed
    yield
    logger.info("Shutting down AI Service...")

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
    """Root endpoint"""
    return {
        "service": "AI LLM Service",
        "status": "running",
        "model": "ollama with Llama3.2:3b",
        "capabilities": ["ocr_correction", "chatbot"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI LLM Service",
        "model": "ollama with Llama3.2:3b"
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
        from .core.ollama_client import OllamaClient
        
        logger.info(f"Received OCR correction request for language: {request.language}")
        
        ollama_client = OllamaClient()
        
        prompt = f"""Fix OCR errors in this {request.language} text. Return only the corrected text without explanations.

Original text:
{request.raw_text}

Corrected text:"""
        
        corrected_text = await ollama_client.generate(prompt)
        
        return OCRCorrectionResponse(
            corrected_text=corrected_text.strip(),
            confidence=0.85,
            language=request.language,
            changes_made=[],
            metadata={"model": "llama3.2:3b", "service": "ai-llm-service"}
        )
        
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
            context=request.context or {}
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/prescription/process")
async def process_prescription(request: dict):
    """
    Process prescription OCR data for mobile app integration
    - Enhances OCR accuracy
    - Generates clean, structured JSON for reminder creation
    - Extracts complete medical information for history
    
    Args:
        request: Dict with 'raw_ocr_json' containing OCR data
        
    Returns:
        Structured prescription data with medications and patient info
    """
    try:
        from .core.ollama_client import OllamaClient
        from .features.prescription.processor import PrescriptionProcessor
        
        raw_ocr_json = request.get("raw_ocr_json", {})
        if not raw_ocr_json:
            raise HTTPException(status_code=400, detail="No OCR data provided")
        
        # Initialize processor
        ollama_client = OllamaClient()
        processor = PrescriptionProcessor(ollama_client)
        
        # Process prescription
        result = processor.process_prescription(raw_ocr_json)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing prescription: {str(e)}")
        return {
            "patient_info": {"name": "", "id": "", "age": None, "gender": "", "hospital_code": ""},
            "medical_info": {"diagnosis": "", "doctor": "", "date": "", "department": ""},
            "medications": [],
            "success": False,
            "error": str(e)
        }

@app.post("/api/v1/prescription/enhance-and-generate-reminders")
async def enhance_and_generate_reminders(request: dict):
    """
    Enhanced prescription processing with automatic reminder generation
    - Processes OCR text using AI
    - Extracts structured prescription data
    - Generates medication reminders with notifications
    - Returns complete data for database insertion
    
    Args:
        request: Dict with:
            - 'ocr_data': OCR output (raw text or structured)
            - 'base_date': Optional start date (YYYY-MM-DD, default: today)
            - 'patient_id': Optional patient identifier
            
    Returns:
        Complete prescription data with generated reminders
    """
    try:
        from .core.ollama_client import OllamaClient
        from .features.prescription.processor import PrescriptionProcessor
        from .features.prescription.enhancer import enhance_prescription
        from .features.prescription.reminder_generator import generate_reminders_from_prescription
        
        ocr_data = request.get("ocr_data", {})
        base_date = request.get("base_date")
        patient_id = request.get("patient_id", "")
        
        if not ocr_data:
            raise HTTPException(status_code=400, detail="No OCR data provided")
        
        logger.info(f"Processing prescription for reminder generation (patient: {patient_id})")
        
        # Step 1: Enhance prescription using AI
        enhanced_result = enhance_prescription(ocr_data)
        
        if not enhanced_result.get("success"):
            logger.warning("AI enhancement failed, attempting basic processing")
            # Fallback to basic processor
            ollama_client = OllamaClient()
            processor = PrescriptionProcessor(ollama_client)
            enhanced_result = {
                "success": True,
                "extracted_data": processor.process_prescription(ocr_data),
                "ai_enhanced": False
            }
        
        # Step 2: Extract prescription data
        prescription_data = enhanced_result.get("extracted_data", {})
        
        if not prescription_data or not prescription_data.get("medications"):
            return {
                "success": False,
                "error": "No medications found in prescription",
                "prescription": prescription_data,
                "reminders": [],
                "metadata": {
                    "ai_enhanced": enhanced_result.get("ai_enhanced", False),
                    "processing_timestamp": datetime.now().isoformat()
                }
            }
        
        # Step 3: Generate reminders
        reminder_result = generate_reminders_from_prescription(prescription_data, base_date)
        
        # Step 4: Build complete response
        response = {
            "success": True,
            "prescription": reminder_result["prescription"],
            "reminders": reminder_result["reminders"],
            "validation": reminder_result["validation"],
            "metadata": {
                "ai_enhanced": enhanced_result.get("ai_enhanced", False),
                "extraction_method": enhanced_result.get("extraction_method", "basic"),
                "model_used": enhanced_result.get("metadata", {}).get("model_used", "unknown"),
                "confidence_score": enhanced_result.get("metadata", {}).get("confidence", 0.0),
                "language_detected": enhanced_result.get("metadata", {}).get("language", "unknown"),
                "processing_timestamp": datetime.now().isoformat(),
                "total_reminders": reminder_result["metadata"]["total_reminders"],
                **reminder_result["metadata"]
            }
        }
        
        logger.info(f"✅ Successfully generated {response['metadata']['total_reminders']} reminders")
        return response
        
    except Exception as e:
        logger.error(f"Error in enhance and generate reminders: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "prescription": {},
            "reminders": [],
            "metadata": {
                "processing_timestamp": datetime.now().isoformat()
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-llm-service"}


@app.post("/api/v1/prescription/unified-reminder")
async def generate_unified_reminder(request: dict):
    """
    Process a single prescription and generate unified JSON for reminders.
    Returns data for user review before final reminder creation.
    
    Response includes `needs_review: true` - user must review/edit data 
    before confirming to generate final reminders.
    
    This endpoint produces the target format:
    {
      "needs_review": true,
      "prescription_data": {
        "patients": [{
          "name": "patient name",
          "source": "hospital name",
          "visit_date": "DD/MM/YYYY",
          "medicines": [{
            "name": "Medication 20mg",
            "total_quantity": 14,
            "unit": "Tablet",
            "reminders": [{
              "time": "Morning",
              "dosage_quantity": 1,
              "dosage_unit": "Tablet",
              "instruction_kh": "លេប ១ គ្រាប់ ក្រោយបាយ"
            }]
          }]
        }]
      }
    }
    
    Args:
        request: Dict with:
            - 'ocr_data': OCR output (raw text or structured) - required
            - 'patient_name': Optional patient name override
            - 'source': Optional hospital/clinic name override
            - 'visit_date': Optional visit date in DD/MM/YYYY format
            
    Returns:
        Unified prescription data with Khmer instructions for user review
    """
    try:
        from .features.prescription.enhancer import enhance_prescription
        from .features.prescription.reminder_generator import generate_unified_reminders
        
        ocr_data = request.get("ocr_data", {})
        
        if not ocr_data:
            raise HTTPException(status_code=400, detail="No OCR data provided. Use 'ocr_data' field.")
        
        logger.info("Processing prescription for unified reminders (user review required)")
        
        # Step 1: Enhance prescription using AI
        enhanced = enhance_prescription(ocr_data)
        
        if not enhanced.get("success"):
            # Fallback to basic processing
            from .core.ollama_client import OllamaClient
            from .features.prescription.processor import PrescriptionProcessor
            
            ollama_client = OllamaClient()
            processor = PrescriptionProcessor(ollama_client)
            extracted_data = processor.process_prescription(ocr_data)
        else:
            extracted_data = enhanced.get("extracted_data", {})
        
        if not extracted_data or not extracted_data.get("medications"):
            return {
                "success": False,
                "needs_review": False,
                "error": "No medications found in prescription",
                "prescription_data": {"patients": []},
                "metadata": {
                    "processing_timestamp": datetime.now().isoformat()
                }
            }
        
        # Step 2: Generate unified reminders with Khmer instructions
        result = generate_unified_reminders(
            prescription_data=extracted_data,
            patient_name=request.get("patient_name", ""),
            source=request.get("source", ""),
            visit_date=request.get("visit_date", "")
        )
        
        # Mark as needs review - user must confirm before generating reminders
        result["needs_review"] = True
        
        # Add enhancement metadata
        result["metadata"]["ai_enhanced"] = enhanced.get("ai_enhanced", False)
        result["metadata"]["extraction_method"] = enhanced.get("extraction_method", "basic")
        result["metadata"]["review_message"] = "Please review and edit prescription data before confirming"
        
        logger.info(f"✅ Generated {result['metadata']['total_reminders']} reminders for review")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating unified reminders: {str(e)}", exc_info=True)
        return {
            "success": False,
            "needs_review": False,
            "error": str(e),
            "prescription_data": {"patients": []},
            "metadata": {
                "processing_timestamp": datetime.now().isoformat()
            }
        }

if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("AI_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_SERVICE_PORT", "8001"))
    uvicorn.run(app, host=host, port=port)
