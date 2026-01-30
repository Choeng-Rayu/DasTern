# AI LLM Service

LLaMA-based medical AI for prescription enhancement and chatbot functionality.

## Architecture

```
ai-llm-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── model_loader.py      # LLaMA model loading
│   │   └── generation.py        # Unified text generation
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── prescription/
│   │   │   ├── __init__.py
│   │   │   ├── enhancer.py      # Prescription enhancement
│   │   │   └── validator.py     # Safety validation
│   │   │
│   │   └── chat/
│   │       ├── __init__.py
│   │       └── assistant.py     # Medical chatbot
│   │
│   └── safety/
│       ├── __init__.py
│       ├── language.py          # Language validation
│       └── medical.py           # Medical safety constraints
│
├── models/
│   └── llama/                   # Put GGUF model files here
│
├── requirements.txt
├── Dockerfile
└── README.md
```

## Prerequisites
- Python 3.10+
- (Optional) GPU drivers/CUDA for faster inference

## Setup
```bash
cd ai-llm-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Download LLaMA Model
Get a quantized GGUF model (e.g., llama-2-7b-chat.Q4_K_M.gguf) and place in `models/llama/` directory.

## Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Open:
- API docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

## API Endpoints

### POST /api/v1/enhance
Enhance prescription from OCR output

**Request:**
```json
{
  "ocr_result": {...},
  "language": "en"
}
```

### POST /api/v1/chat
Chat with medical assistant

**Request:**
```json
{
  "message": "What is this medicine for?",
  "history": [],
  "context": {...},
  "language": "en"
}
```

### POST /api/v1/validate
Validate prescription data

**Request:**
```json
{
  "prescription_data": {...}
}
```

## Implementation Status

🚧 **Structure Ready - Implementation Pending**

All files are created with TODO markers for implementation.

## Key Features

✅ Two distinct roles:
- **Prescription Enhancer**: Clean OCR → Normalized data
- **Medical Chatbot**: Answer questions safely

✅ Safety constraints:
- No diagnosis
- No prescription recommendations
- Medical disclaimer on all outputs

## Next Steps

1. Implement model loading in `model_loader.py`
2. Create generation logic in `generation.py`
3. Build prescription enhancer in `enhancer.py`
4. Add safety validators in `validator.py` and `medical.py`
5. Implement chatbot in `assistant.py`
6. Test with sample OCR outputs