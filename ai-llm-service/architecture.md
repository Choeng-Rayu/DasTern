# AI-LLM Service Architecture

## Overview

The AI-LLM service is a multi-layered architecture designed to process medical prescriptions using OCR and LLM-powered extraction and analysis. The system follows a clean architecture pattern with clear separation of concerns across distinct layers.

---

## Architecture Layers

### 1. **API Layer** (`app/`)

**Purpose:** Handles all HTTP requests and routes them to appropriate business logic.

**Components:**
- `main.py` / `main_ollama.py` - FastAPI application initialization
- `api/extraction_routes.py` - REST endpoints for OCR processing and extraction

**Responsibilities:**
- Accept incoming HTTP requests
- Validate request parameters
- Route requests to business logic layer
- Return JSON responses

**Public Endpoints:**
- `/extract` - Extract prescription data from OCR
- `/remind` - Generate medication reminders
- `/validate` - Validate prescription information

---

### 2. **Business Logic Layer** (`app/features/`)

**Purpose:** Implements core domain features and workflows.

**Components:**

#### **Prescription Processing**
- `prescription/processor.py` - Main prescription processing orchestrator
- `prescription/enhancer.py` - Enhances extracted prescription data
- `prescription/fast_parser.py` - Fast parsing of prescription text
- `prescription/khmer_instructions.py` - Khmer language instruction generation

**Responsibilities:**
- Coordinate prescription data extraction
- Enhance and format prescription information
- Generate Khmer language instructions for patients
- Manage prescription workflows

#### **Reminder Engine**
- `reminder_engine.py` - Generates medication reminders

**Responsibilities:**
- Create reminder schedules based on prescriptions
- Manage reminder notifications
- Track reminder delivery

---

### 3. **Core Processing Layer** (`app/core/`)

**Purpose:** Manages AI models and inference operations.

**Components:**

#### **Model Management**
- `model_loader.py` - Loads and caches LLM models
- Supported models: Ollama-based models (3B, 7B, 13B variants)

**Responsibilities:**
- Load models from Ollama service
- Manage model caching for performance
- Handle model version management

#### **Ollama Integration**
- `ollama_client.py` - Client for Ollama LLM service
- `generation.py` - LLM generation and inference engine

**Responsibilities:**
- Communicate with Ollama service
- Execute LLM inference
- Handle model inference parameters
- Manage response parsing

#### **Data Extraction**
- `finetuned_extractor.py` - Uses finetuned models for structured extraction

**Responsibilities:**
- Extract structured information from text
- Apply finetuning-specific extraction patterns
- Return validated extraction results

---

### 4. **Safety & Validation Layer** (`app/safety/`)

**Purpose:** Ensures data safety and medical accuracy.

**Components:**

#### **Medical Validation**
- `medical.py` - Medical information validator
  - Validates drug names and interactions
  - Checks dosage appropriateness
  - Verifies medical terms accuracy

#### **Language Safety**
- `language.py` - Language and content safety checker
  - Validates Khmer language output
  - Checks for inappropriate content
  - Verifies language accuracy

#### **Prescription Validation**
- `prescription/validator.py` - Prescription-specific validation
  - Validates extracted prescription structure
  - Checks required fields
  - Verifies data consistency

---

### 5. **Data Layer** (`data/`)

**Purpose:** Persistent storage and data management.

**Storage Types:**
- **JSON Files** - Extracted OCR results and processed data
- **Database** - Prescription and reminder records (future)

**Data Stored:**
- `extracted_ocr_result_*.json` - Raw OCR extraction outputs
- `ocr_result_*.json` - Processed OCR results
- `reports/` - Validation and correction reports

---

### 6. **External Services**

#### **Ollama LLM Service**
- Provides language model inference
- Hosted on configurable port (default: 11434)
- Supports multiple model variants

#### **Tesseract OCR**
- Optical Character Recognition service
- Extracts text from prescription images
- Provides raw text for LLM processing

---

## Layer Communication Flow

### Request Processing Flow

```
Client Request
    ↓
API Layer (extraction_routes.py)
    ↓
Business Logic Layer (prescription_processor.py)
    ├─→ Khmer Instructions Engine
    └─→ Reminder Engine
    ↓
Core Processing Layer
    ├─→ Model Loader (requests model from Ollama)
    ├─→ Finetuned Extractor
    └─→ Generation Engine (LLM inference)
    ↓
Safety & Validation Layer
    ├─→ Medical Validator
    ├─→ Language Safety
    └─→ Prescription Validator
    ↓
Data Layer (persistence)
    ↓
Response to Client
```

### Detailed Communication Patterns

#### **1. API → Business Logic**
```
HTTP Request (OCR image + metadata)
  ↓
extraction_routes.py validates input
  ↓
prescription_processor.py receives request
  ↓
Routes to appropriate processor
```

#### **2. Business Logic → Core Processing**
```
processor.py requests model
  ↓
model_loader.py loads from Ollama
  ↓
generation.py prepares LLM prompt
  ↓
ollama_client.py sends to Ollama service
  ↓
Response with LLM output
```

#### **3. Core Processing → Safety Validation**
```
Generated/extracted data
  ↓
medical.py validates medical accuracy
  ↓
language.py validates Khmer output
  ↓
validator.py checks prescription structure
  ↓
Returns validation result to business logic
```

#### **4. Business Logic → Data Layer**
```
Validated prescription data
  ↓
Stored in data/reports/ or database
  ↓
Confirmation of storage
```

---

## Data Flow Example: Prescription Processing

```
1. IMAGE INPUT
   └─ User uploads prescription image
   
2. API LAYER
   └─ /extract endpoint receives image
   
3. TESSERACT OCR
   └─ Extracts text from image
   
4. BUSINESS LOGIC
   ├─ fast_parser.py parses raw text
   ├─ processor.py initiates processing
   └─ enhancer.py enriches data
   
5. CORE PROCESSING
   ├─ model_loader.py loads LLM model
   ├─ generation.py generates prompts
   ├─ ollama_client.py calls Ollama service
   └─ finetuned_extractor.py extracts structured data
   
6. SAFETY & VALIDATION
   ├─ medical.py validates drugs and dosages
   ├─ language.py validates Khmer instructions
   └─ validator.py checks prescription completeness
   
7. OUTPUT GENERATION
   ├─ khmer_instructions.py creates patient instructions
   └─ reminder_engine.py generates reminders
   
8. DATA PERSISTENCE
   └─ Results stored in data/ directory
   
9. API RESPONSE
   └─ Returns JSON with extracted data, reminders, instructions
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI (Python) |
| **LLM Service** | Ollama (Local/Remote) |
| **OCR** | Tesseract |
| **Data Storage** | JSON, PostgreSQL (future) |
| **Language** | Python 3.8+ |
| **Async Support** | AsyncIO |

---

## Component Responsibilities Summary

| Component | Responsibility | Input | Output |
|-----------|-----------------|-------|--------|
| `extraction_routes.py` | HTTP routing | HTTP Request | HTTP Response |
| `prescription_processor.py` | Orchestration | Raw OCR text | Processed prescription |
| `model_loader.py` | Model management | Model name | Loaded model |
| `ollama_client.py` | LLM communication | Prompt | LLM response |
| `finetuned_extractor.py` | Data extraction | Text + model | Structured JSON |
| `medical.py` | Medical validation | Drug/dosage data | Validation result |
| `language.py` | Safety checking | Generated text | Safety report |
| `validator.py` | Structure validation | Extracted data | Validation errors |
| `reminder_engine.py` | Reminder creation | Prescription | Reminder schedule |
| `khmer_instructions.py` | Instruction generation | Drug info | Khmer text |

---

## Configuration & Environment

**Key Configuration Variables:**
- `OLLAMA_HOST` - Ollama service endpoint (default: localhost:11434)
- `MODEL_NAME` - LLM model to use (e.g., "mistral", "neural-chat")
- `API_PORT` - FastAPI port (default: 8000)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING)

**Environment Files:**
- `.env` - Runtime configuration
- `.env.example` - Configuration template

---

## Error Handling

Each layer implements error handling:
- **API Layer** - HTTP exception handling, request validation
- **Business Logic** - Workflow error handling, retry logic
- **Core Processing** - Model loading errors, inference timeouts
- **Validation Layer** - Validation error reporting with details
- **Data Layer** - Storage failure handling, recovery

---

## Performance Considerations

1. **Model Caching** - Models cached in memory to reduce loading overhead
2. **Async Operations** - FastAPI async endpoints for non-blocking requests
3. **Batch Processing** - Support for batch prescription processing
4. **Prompt Optimization** - Optimized prompts for faster LLM inference
5. **Data Validation** - Early validation to prevent downstream errors

---

## Security

- **Input Validation** - All inputs validated at API layer
- **Medical Accuracy** - Safety validation before output
- **Language Safety** - Content filtering in language layer
- **Error Messages** - Generic error responses to prevent information leakage

---

## Scalability & Future Enhancements

1. **Database Integration** - PostgreSQL for persistent storage
2. **Caching Layer** - Redis for caching frequent operations
3. **Queue System** - Celery for async task processing
4. **Load Balancing** - Deploy multiple instances behind load balancer
5. **Model Switching** - Support for multiple LLM models
6. **Webhook Support** - Real-time processing notifications

---

## Development Guidelines

### Adding a New Feature

1. **Define API endpoint** in `api/extraction_routes.py`
2. **Implement business logic** in `features/`
3. **Use core processing** components for AI operations
4. **Add validation** in `safety/` layer
5. **Persist data** through data layer
6. **Write tests** in `tests/`

### Debugging

- Check logs in `ollama_log.txt`
- Enable `DEBUG` log level for detailed output
- Monitor Ollama service health
- Validate OCR output before processing

---

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama service running
- Tesseract OCR installed

### Installation
```bash
pip install -r requirements.txt
```

### Running the Service
```bash
python app/main_ollama.py
```

### API Testing
```bash
curl -X POST http://localhost:8000/extract \
  -F "image=@prescription.jpg"
```

---

## Architecture Diagram

Refer to `architecture.puml` for the visual representation of layer interactions and communication flows.

---

## Support & Documentation

- `QUICK_START.md` - Quick start guide
- `QUICKSTART_3B.md` - 3B model optimization guide
- `TECHNICAL_DETAILS_3B.md` - Technical optimization details
- `docs/` - Additional documentation
