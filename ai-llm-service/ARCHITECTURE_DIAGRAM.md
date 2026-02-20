# AI-LLM Service Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (External)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Mobile App (Flutter) | Web Client | Backend Services | External Systems    │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │ HTTP/HTTPS Requests
                                         ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│              API LAYER & REQUEST ROUTING (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  extraction_routes.py                                                │   │
│  │  - /extract              (Process OCR & Extract Prescription)        │   │
│  │  - /validate             (Validate Prescription Data)                │   │
│  │  - /remind               (Generate Medication Reminders)             │   │
│  │  - /health               (Service Health Check)                      │   │
│  │                                                                      │   │
│  │  Features: Request Validation, CORS, Error Handling                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ↓                        ↓                        ↓
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  BUSINESS LOGIC L.   │ │  SAFETY & VALIDATION │ │  EXTERNAL SERVICES   │
│ (features/)          │ │  (safety/)           │ │  INTEGRATION         │
│                      │ │                      │ │                      │
│ • processor.py       │ │ • medical.py         │ │ • Oligma LLM         │
│   - Orchestration    │ │   (Drug validation)  │ │   (Model Inference)  │
│                      │ │                      │ │                      │
│ • enhancer.py        │ │ • language.py        │ │ • Tesseract OCR      │
│   (Data Enrichment)  │ │   (Safety Checks)    │ │   (Text Extraction)  │
│                      │ │                      │ │                      │
│ • fast_parser.py     │ │ • validator.py       │ │ COMMUNICATION:       │
│   (Quick Parsing)    │ │   (Structure Chk)    │ │ - REST API Calls     │
│                      │ │                      │ │ - JSON Responses     │
│ • reminder_engine.py │ │ WORKFLOW:            │ │                      │
│   (Reminder Gen)     │ │ Input Validation     │ │                      │
│                      │ │ ↓ Process Data       │ │                      │
│ • khmer_instructions │ │ ↓ Safety Checks      │ │                      │
│   (Khmer Output)     │ │ ↓ Return Data        │ │                      │
└──────────┬───────────┘ └──────┬───────────────┘ └──────────┬───────────┘
           │                    │                            │
           └────────────────────┼────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│               CORE PROCESSING LAYER (app/core/)                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ model_loader.py                                                      │   │
│  │  ├─ Load LLM Models from Ollama                                      │   │
│  │  ├─ Cache Models in Memory                                           │   │
│  │  └─ Model Manager & Lifecycle                                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ollama_client.py & generation.py                                     │   │
│  │  ├─ LLM Inference Management                                         │   │
│  │  ├─ Prompt Engineering & Optimization                                │   │
│  │  ├─ Response Parsing                                                 │   │
│  │  └─ Error Handling & Retries                                         │   │
│  └────────────────────┬─────────────────────────────────────────────────┘   │
│                       │                                                     │
│  ┌────────────────────┴─────────────────────────────────────────────────┐   │
│  │ finetuned_extractor.py                                               │   │
│  │  ├─ Structured Data Extraction                                       │   │
│  │  ├─ Pattern Recognition                                              │   │
│  │  ├─ Field Validation                                                 │   │
│  │  └─ Output Formatting (JSON)                                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└────────┬──────────────────────────────────────────────────────────────┬─────┘
         │                                                              │
         │                    PROCESSES                                 │
         │  1. Load Model ──→ 2. Parse Input ──→ 3. Generate Prompt     │
         │  4. LLM Inference ──→ 5. Extract Data ──→ 6. Validate        │
         │                                                              │
         ↓                                                              ↓
┌───────────────────────────────┐                      ┌───────────────────────────────┐
│  OLLAMA LLM SERVICE           │                      │  TESSERACT OCR SERVICE        │
│  (External Service Port 11434)│                      │  (External Service)           │
├───────────────────────────────┤                      ├───────────────────────────────┤
│  • Model: mistral/neural-chat │                      │  • Text Recognition           │
│  • Inference Engine           │                      │  • Handwriting Support        │
│  • Context Management         │                      │  • Multiple Languages         │
│  • Response Streaming (opt.)  │                      │  • Confidence Scores          │
└───────────────────────────────┘                      └───────────────────────────────┘
```

---

## Detailed Layer Communication Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    1. CLIENT REQUEST FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Client sends HTTP POST request with prescription image                     │
│                         │                                                   │
│                         ↓                                                   │
│         ┌───────────────────────────────────────┐                          │
│         │   API LAYER - extraction_routes.py   │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Receives request                    │                          │
│         │ • Validates input parameters          │                          │
│         │ • Extracts image data                 │                          │
│         │ • Error handling & CORS check         │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ BUSINESS LOGIC - processor.py         │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Call Tesseract OCR service          │                          │
│         │ • Extract raw text from image         │                          │
│         │ • Pass to fast_parser for processing  │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ CORE - model_loader & generation.py  │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Load model from Ollama              │                          │
│         │ • Create optimized prompt             │                          │
│         │ • Send prompt to LLM inference        │                          │
│         │ • Receive LLM output                  │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ CORE - finetuned_extractor.py         │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Parse LLM response                  │                          │
│         │ • Extract structured data             │                          │
│         │ • Format as JSON                      │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ VALIDATION - safety/medical.py        │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Validate drug names                 │                          │
│         │ • Check dosage appropriateness        │                          │
│         │ • Verify medical accuracy             │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ VALIDATION - safety/language.py       │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Check content safety                │                          │
│         │ • Validate language output            │                          │
│         │ • Verify Khmer text quality           │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ BUSINESS LOGIC - khmer_instructions  │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Generate patient instructions       │                          │
│         │ • Create medication reminders         │                          │
│         │ • Format output                       │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ DATA LAYER - Storage                  │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Save prescription data              │                          │
│         │ • Store reminders                     │                          │
│         │ • Log processing results              │                          │
│         └───────────────────┬───────────────────┘                          │
│                             │                                              │
│                             ↓                                              │
│         ┌───────────────────────────────────────┐                          │
│         │ API LAYER - Response Handler          │                          │
│         ├───────────────────────────────────────┤                          │
│         │ • Format JSON response                │                          │
│         │ • Include metadata & status           │                          │
│         │ • Return to client                    │                          │
│         └───────────────────────────────────────┘                          │
│                                                                             │
│  Response contains:                                                        │
│  - Extracted prescription data                                             │
│  - Khmer language instructions                                             │
│  - Medication reminders                                                    │
│  - Validation status & errors (if any)                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Persistence Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    File System Storage (data/)                       │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  JSON Files (OCR & Processing Results)                        │ │   │
│  │  │  • extracted_ocr_result_*.json    (Raw OCR outputs)           │ │   │
│  │  │  • ocr_result_*.json              (Processed results)         │ │   │
│  │  │  • tesseract_result_*.json        (Tesseract outputs)         │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  Reports & Logs (data/reports/)                               │ │   │
│  │  │  • correction_report_*.json       (Validation reports)        │ │   │
│  │  │  • processing_log_*.json          (Processing logs)           │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  Training Data (data/training/)                               │ │   │
│  │  │  • finetuning_dataset.jsonl       (Finetuning data)           │ │   │
│  │  │  • model_cache/                   (Cached models)             │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │           Database (PostgreSQL - Future Integration)                │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  prescriptions_table                                          │ │   │
│  │  │  • prescription_id (PK)                                       │ │   │
│  │  │  • patient_id                                                │ │   │
│  │  │  • extracted_data (JSONB)                                    │ │   │
│  │  │  • validation_status                                         │ │   │
│  │  │  • created_at, updated_at                                    │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  reminders_table                                              │ │   │
│  │  │  • reminder_id (PK)                                           │ │   │
│  │  │  • prescription_id (FK)                                       │ │   │
│  │  │  • reminder_text                                              │ │   │
│  │  │  • schedule_time                                              │ │   │
│  │  │  • delivered (boolean)                                        │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete System Integration

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE SYSTEM FLOW                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   EXTERNAL SYSTEMS          │   AI-LLM SERVICE INTERNAL              │ DATA  │
│   ───────────────           │   ──────────────────────               │ ────  │
│                             │                                        │       │
│   📱 Mobile/Web App   ──────┼──→ FastAPI Routes ──┐                │       │
│                             │                    │                 │       │
│   🖼️  OCR Service    ───────┼──────────┐          ↓                 │       │
│   (Tesseract)               │          │   Business Logic Layer     │       │
│                             │          │   • Processor              │       │
│                             │          │   • Enhancer               │       │
│   🧠 LLM Service    ────────┼──────────┼──→ • Fast Parser     ──┐   │       │
│   (Ollama 11434)            │          │   • Reminder Engine   │   │       │
│                             │          │   • Khmer Generator   │   │       │
│                             │          │                       │   │       │
│                             │          ↓                       │   │       │
│                             │   Safety & Validation Layer      │   │       │
│                             │   • Medical Validator            │   │       │
│   📊 External Services ────┤   • Language Safety              │   │       │
│   • Email (SMTP)            │   • Prescription Validator       │   │       │
│   • Payment (Bakong)        │                                  ↓   │       │
│   • Logging                 │   Core Processing Layer         │    │       │
│                             │   • Model Loader                │    │       │
│                             │   • Ollama Client               │    │       │
│                             │   • Generation Engine           │    │       │
│                             │   • Finetuned Extractor         │    │       │
│                             │                                 ↓    │       │
│                             │                             JSON    │ 💾     │
│                             └─────────────────────────────→ Data ─├─→ File │
│                                                            Store  │ System │
│                                                                   │       │
│                                                                   │ (DB)  │
│                                                                   │       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTER-COMPONENT COMMUNICATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Component              Calls                      Frequency     Latency    │
│  ─────────────────────────────────────────────────────────────────────     │
│                                                                              │
│  extraction_routes ──→ processor.py              Per request      Low       │
│  processor.py ───────→ tesseract OCR            Per image       Medium      │
│  processor.py ───────→ model_loader.py          Per request      Low       │
│  processor.py ───────→ enhancer.py              Per result       Low       │
│  model_loader.py ────→ ollama_client.py         Cache hit        Low       │
│  generation.py ──────→ ollama LLM service       Per inference    High       │
│  finetuned_extractor ─→ generation output      Per inference     Low       │
│  medical.py ─────────→ validation rules        Per extraction    Low       │
│  language.py ────────→ Khmer text check        Per output        Low       │
│  validator.py ───────→ schema definitions      Per data          Low       │
│  reminder_engine ────→ generation.py           Per prescription   Low       │
│  processor.py ───────→ data storage            Per completion    Medium      │
│  reminder_engine ────→ data storage            Per reminder      Medium      │
│                                                                              │
│  Legend:                                                                    │
│  Low:    < 100ms (In-memory, local operations)                             │
│  Medium: 100ms - 500ms (File I/O, network hops)                            │
│  High:   > 500ms (External service calls, complex operations)              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling & Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Error Occurs at Layer X                                                   │
│                 │                                                           │
│                 ↓                                                           │
│    ┌────────────────────────────────────┐                                  │
│    │  Layer-Specific Error Handling     │                                  │
│    │  • Log error with context          │                                  │
│    │  • Determine error severity        │                                  │
│    │  • Attempt local recovery          │                                  │
│    └────────────────────┬───────────────┘                                  │
│                         │                                                  │
│          ┌──────────────┴──────────────┐                                   │
│          ↓                             ↓                                   │
│    ┌─────────────────┐          ┌──────────────────┐                      │
│    │ RECOVERABLE     │          │ UNRECOVERABLE    │                      │
│    │ • Retry logic   │          │ • Log full error │                      │
│    │ • Circuit break │          │ • Store in data/ │                      │
│    │ • Fallback mode │          │ • Return 5xx     │                      │
│    │ • Continue flow │          │ • Alert (future) │                      │
│    └────────┬────────┘          └──────────┬───────┘                      │
│             │                              │                              │
│             └──────────────┬───────────────┘                               │
│                            ↓                                               │
│          ┌─────────────────────────────────┐                              │
│          │ Return Error Response to Client │                              │
│          │ {                               │                              │
│          │   "status": "error",            │                              │
│          │   "message": "User-friendly",   │                              │
│          │   "error_code": "VALIDATION",   │                              │
│          │   "details": {...}              │                              │
│          │ }                               │                              │
│          └─────────────────────────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Performance Optimization Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE & CACHING STRATEGY                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Level 1: In-Memory Caching (Model Loader)                          │   │
│  │  ├─ Loaded LLM models stay in memory                                │   │
│  │  ├─ Reuse model across requests                                     │   │
│  │  ├─ Warm-up models on service startup                              │   │
│  │  └─ Avoid model reload latency (>5s per model)                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Level 2: Request Response Caching                                   │   │
│  │  ├─ Cache identical OCR extraction requests                          │   │
│  │  ├─ Cache validation rules                                           │   │
│  │  ├─ TTL-based automatic invalidation                                 │   │
│  │  └─ Hash-based request matching                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Level 3: Batch Processing                                           │   │
│  │  ├─ Queue multiple requests                                          │   │
│  │  ├─ Process in batches for better LLM throughput                    │   │
│  │  ├─ Reduce context switching                                         │   │
│  │  └─ Optimize Ollama inference efficiency                             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Level 4: Async & Non-Blocking Operations                            │   │
│  │  ├─ FastAPI async endpoints                                          │   │
│  │  ├─ Non-blocking I/O for file operations                             │   │
│  │  ├─ Concurrent request handling                                      │   │
│  │  └─ Handle 10+ concurrent users efficiently                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Level 5: Resource Management                                        │   │
│  │  ├─ Limit concurrent Ollama calls (single GPU)                       │   │
│  │  ├─ Queue management for fair access                                 │   │
│  │  ├─ Memory monitoring & cleanup                                      │   │
│  │  └─ Graceful degradation under load                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT & SCALABILITY                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Development                Production (Single Server)                      │
│  ───────────────           ──────────────────────────                       │
│                                                                              │
│  ┌──────────────────┐      ┌─────────────────────────────────┐             │
│  │ FastAPI Server   │      │  🐳 Docker Container            │             │
│  │ (localhost:8000) │      ├─────────────────────────────────┤             │
│  │                  │      │  ┌─ FastAPI Service (8000)     │             │
│  │ Ollama LLM       │      │  ├─ Ollama Service (11434)      │             │
│  │ (localhost:11434)│      │  ├─ File Storage (/data)        │             │
│  │                  │      │  └─ Logs (./logs)               │             │
│  │ File-based Data  │      │                                 │             │
│  │ (JSON)           │      │  Volume Mounts:                 │             │
│  │                  │      │  • Data persistence             │             │
│  │ Local Tesseract  │      │  • Log collection               │             │
│  └──────────────────┘      │  • Model cache                  │             │
│                            │                                 │             │
│                            │  Resources:                     │             │
│                            │  • 4 CPU cores                  │             │
│                            │  • 8GB RAM (Ollama + Cache)     │             │
│                            │  • GPU (optional, CUDA)         │             │
│                            │  • 50GB storage                 │             │
│                            └─────────────────────────────────┘             │
│                                         │                                  │
│                                         ↓                                  │
│                            ┌──────────────────────┐                        │
│                            │  Reverse Proxy/      │                        │
│                            │  Load Balancer       │                        │
│                            │  (Nginx)             │                        │
│                            │  Port 80/443         │                        │
│                            └──────────────────────┘                        │
│                                         │                                  │
│                                         ↓                                  │
│                            ┌──────────────────────┐                        │
│                            │  External World      │                        │
│                            │  Mobile Apps         │                        │
│                            │  Web Clients         │                        │
│                            │  Backend Services    │                        │
│                            └──────────────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Service Dependencies & Port Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              SERVICE DEPENDENCIES & COMMUNICATION PORTS                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Service              Port    Protocol    Status        Dependency          │
│  ─────────────────────────────────────────────────────────────────────     │
│                                                                              │
│  FastAPI Server      8000    HTTP/HTTPS  REQUIRED      Main service        │
│  Ollama LLM Service  11434   HTTP        REQUIRED      AI inference        │
│  Tesseract OCR       N/A     Shell exec  REQUIRED      Text extraction     │
│  PostgreSQL          5432    TCP         OPTIONAL      Future DB            │
│  Redis Cache         6379    TCP         OPTIONAL      Future cache         │
│  Email Service       587     SMTP        OPTIONAL      Future notifications│
│                                                                              │
│  Communication Patterns:                                                   │
│  • Localhost communication for services on same machine                     │
│  • JSON over HTTP for external APIs                                         │
│  • Shell exec for Tesseract integration                                     │
│  • Async/await for non-blocking calls                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```
