# DasTern V2 - Medical Prescription OCR System

## 📁 FINAL MONOREPO STRUCTURE (RECOMMENDED)

```
dastern-v2/
├── apps/
│   ├── mobile-flutter/
│   │   └── lib/
│   ├── backend-nextjs/
│   │   ├── app/
│   │   │   └── api/
│   │   │       ├── ocr/
│   │   │       ├── ai/
│   │   │       ├── chat/
│   │   │       └── users/
│   │   ├── lib/
│   │   └── prisma/
│   ├── ocr-service/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── pipeline.py
│   │   │   ├── quality.py
│   │   │   ├── preprocess.py
│   │   │   ├── layout.py
│   │   │   ├── ocr_engine.py
│   │   │   ├── postprocess.py
│   │   │   ├── confidence.py
│   │   │   └── schemas.py
│   │   ├── tessdata/
│   │   └── requirements.txt
│   └── ai-llm-service/
│       ├── app/
│       │   ├── main.py
│       │   ├── model_loader.py
│       │   ├── ocr_corrector.py
│       │   ├── chat_assistant.py
│       │   ├── prompts/
│       │   │   ├── ocr_fix.txt
│       │   │   ├── chatbot.txt
│       │   │   └── medical_help.txt
│       │   ├── schemas.py
│       │   └── confidence.py
│       ├── models/
│       │   └── mt5-small/
│       ├── fine_tune/
│       └── requirements.txt
├── shared/
│   ├── types/
│   └── constants/
└── docs/
   └── architecture.md
```
---

## 🎯 ROLE OF EACH SERVICE (CLEAR & NON-OVERLAPPING)

### 1️⃣ OCR SERVICE (Python – OpenCV + Tesseract)

**📁 apps/ocr-service**

**Responsibilities**
- Image quality check
- Image preprocessing
- Layout detection
- OCR text extraction
- Basic rule cleanup
- Confidence estimation

**Does NOT**
- ❌ Run MT5
- ❌ Understand meaning
- ❌ Chat with users

**📌 Output = raw but clean text**

---

### 2️⃣ AI LLM SERVICE (MT5)

**📁 apps/ai-llm-service**

**Responsibilities**
- OCR error correction
- Multilingual normalization (KH / EN / FR)
- Medical text understanding
- Chatbot assistance
- Question answering
- Explanation to users

**Does NOT**
- ❌ Process images
- ❌ Handle OpenCV
- ❌ Do OCR

**📌 Input = text only**

---

### 3️⃣ NEXT.JS BACKEND (Orchestrator)

**📁 apps/backend-nextjs**

**Responsibilities**
- User authentication
- API gateway
- Call OCR service
- Call AI service
- Manage workflow
- Save results
- Serve Flutter

**📌 This is your control tower**

---

### 4️⃣ FLUTTER APP (UI)

**📁 apps/mobile-flutter**

**Responsibilities**
- Capture image
- Upload image
- Show OCR preview
- Chat with AI assistant
- Confirm data

**📌 Zero intelligence here (by design)**

---

## 🔄 REAL REQUEST FLOW (IMPORTANT)

### OCR Flow
```
Flutter → Next.js → OCR Service
OCR Service → raw text
Next.js → AI LLM Service (optional)
AI Service → enhanced text
Next.js → Flutter
```

### Chatbot Flow
```
Flutter → Next.js → AI LLM Service
AI LLM Service → response
Next.js → Flutter
```

📌 OCR can work without AI
📌 AI can work without OCR

---

## 🧠 WHY THIS DESIGN? (Defense Strategy)

### **Question**: "Why separate services?"

**Answer**:
> "We separated OCR and AI services to follow the single-responsibility principle. OCR focuses on visual text extraction, while MT5 handles multilingual language understanding and user assistance. This design improves performance, scalability, and future extensibility."

### **Question**: "Why not do OCR in the mobile app?"

**Answer**:
> "Performing OCR on mobile would consume excessive battery, require large AI model downloads, and provide inconsistent results across devices. By processing on the server, we ensure consistent quality, can use more powerful models, and keep the mobile app lightweight and responsive."

### **Question**: "Why use Next.js instead of pure Node/Express?"

**Answer**:
> "Next.js provides TypeScript safety, built-in API routes, server-side rendering for admin dashboards, and excellent deployment options. It's a modern full-stack framework that reduces boilerplate while maintaining flexibility."

---

## ⚙️ DEPLOYMENT STRATEGY (SIMPLE)

| Component | Platform | Purpose |
|-----------|----------|---------|
| Flutter App | Play Store / APK | End-user mobile application |
| Next.js Backend | VPS / Vercel | API gateway and workflow |
| OCR Service | VPS (CPU) | Image processing + OCR |
| AI LLM Service | VPS (CPU/GPU) | MT5 correction + chatbot |
| Database | PostgreSQL | Persistent storage |

---

## 🚀 QUICK START (PATHS UPDATED)

### Prerequisites
- Node.js 18+ (for Next.js backend)
- Python 3.9+ (for OCR backend)
- Flutter 3.0+ (for mobile app)
- PostgreSQL (for database)

### Quick Start

1. **Next.js Backend**
   ```bash
   cd apps/backend-nextjs
   npm install
   npm run dev
   ```

2. **OCR Service**
   ```bash
   cd apps/ocr-service
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

3. **AI LLM Service**
   ```bash
   cd apps/ai-llm-service
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8001
   ```

4. **Flutter App**
   ```bash
   cd apps/mobile-flutter
   flutter pub get
   flutter run
   ```

---

## 📚 Documentation

- docs/architecture.md

---

## 🏗️ Architecture Principles

✅ **Separation of Concerns** - Each service has a single, well-defined responsibility

✅ **Stateless Services** - OCR backend doesn't store data, making it easy to scale

✅ **Type Safety** - TypeScript in Next.js, Pydantic in Python for data validation

✅ **Scalability** - Each component can be scaled independently

✅ **Maintainability** - Clear boundaries make debugging and updates easier

---

## 📄 License

[Add your license here]

## 👥 Contributors

[Add contributors here]