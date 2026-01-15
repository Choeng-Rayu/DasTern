# DasTern - Medical Prescription OCR System

## 📁 MONOREPO PROJECT STRUCTURE

```
dastern/
├── mobile_app/                 # Flutter Mobile Application
│   ├── lib/
│   │   ├── screens/           # UI screens
│   │   ├── widgets/           # Reusable widgets
│   │   ├── services/          # API services
│   │   ├── models/            # Data models
│   │   └── main.dart          # Entry point
│   ├── android/               # Android config
│   ├── ios/                   # iOS config
│   └── pubspec.yaml           # Dependencies
│
├── backend/                    # Next.js Backend (API Gateway)
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── auth/          # Authentication
│   │   │   ├── ocr/           # OCR endpoints
│   │   │   ├── review/        # Review system
│   │   │   └── users/         # User management
│   │   ├── dashboard/         # Admin dashboard
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   ├── lib/                   # Utilities
│   │   ├── db.ts              # Database connection
│   │   ├── ocr-client.ts      # OCR backend client
│   │   └── auth.ts            # Auth utilities
│   ├── prisma/                # Database schema
│   ├── package.json
│   └── next.config.ts
│
├── OCR_System/
│   └── ocr-backend/           # Python OCR + AI Engine
│       ├── app/
│       │   ├── main.py        # FastAPI entry
│       │   ├── pipeline.py    # OCR pipeline
│       │   ├── quality.py     # Image quality check
│       │   ├── preprocess.py  # OpenCV preprocessing
│       │   ├── layout.py      # Layout detection
│       │   ├── ocr_engine.py  # Tesseract OCR
│       │   ├── ai_corrector.py # MT5 correction
│       │   ├── postprocess.py # Text cleanup
│       │   ├── confidence.py  # Confidence scoring
│       │   └── schemas.py     # Pydantic models
│       │
│       ├── ai/                # AI models
│       │   └── mt5/
│       │       ├── tokenizer/ # MT5 tokenizer
│       │       └── model/     # MT5 model files
│       │
│       ├── tessdata/          # Tesseract language data
│       ├── requirements.txt
│       └── README.md
│
└── AI/                        # AI Training & Development
    ├── train.py               # Model training
    ├── healthcare_lnp.py      # Healthcare LNP model
    ├── healthcare_lnp_model.pth # Trained model
    ├── app.py                 # Demo application
    └── requirements.txt
```

---

## 🎯 ROLE OF EACH COMPONENT

### 1️⃣ Flutter App (`mobile_app/`) - User Interface

**📱 Role**: Mobile application for end users (pharmacists, doctors, patients)

**Responsibilities**:
- ✅ Capture prescription images
- ✅ Upload to backend
- ✅ Display OCR preview
- ✅ Allow user corrections
- ✅ Confirm final results
- ✅ User authentication UI

**Does NOT**:
- ❌ No OCR processing
- ❌ No AI logic
- ❌ No image preprocessing

**📌 Benefit**: Keeps app fast, lightweight, and responsive

---

### 2️⃣ Next.js Backend (`backend/`) - API Gateway & Controller

**🔧 Role**: System orchestrator and workflow manager

**Responsibilities**:
- ✅ User authentication & authorization
- ✅ File upload handling
- ✅ Call OCR + AI backend
- ✅ Database operations (save results, track status)
- ✅ Manage review workflow
- ✅ Serve data to Flutter app
- ✅ Admin dashboard (optional)

**Request Flow**:
```
Flutter → /api/ocr/upload
Next.js → OCR Backend (Python)
OCR Backend → JSON response
Next.js → Save to database
Next.js → Return to Flutter
```

**Why Next.js?**
- TypeScript type safety
- Built-in API routes
- Can serve admin dashboard
- Easy deployment (Vercel/VPS)
- Excellent scalability

---

### 3️⃣ OCR + AI Backend (`OCR_System/ocr-backend/`) - Intelligence Engine

**🧠 Role**: Pure computational processing engine

**Responsibilities**:
- ✅ Image quality gate (reject blurry images)
- ✅ OpenCV preprocessing (deskew, denoise, binarization)
- ✅ Layout detection (find text regions)
- ✅ Tesseract OCR (extract text)
- ✅ MT5 AI correction (fix errors, normalize language)
- ✅ Confidence scoring
- ✅ Return structured JSON

**Does NOT**:
- ❌ No user management
- ❌ No authentication
- ❌ No database operations
- ❌ No UI logic

**📌 Why Separate?**
- Python excels at image processing (OpenCV)
- AI/ML models (PyTorch, Transformers)
- Stateless service = easy scaling
- Can be deployed independently

---

### 4️⃣ AI MT5 Model (`OCR_System/ocr-backend/ai/mt5/`) - Error Correction

**🤖 Role**: OCR text correction and normalization

**Responsibilities**:
- ✅ Correct OCR errors (e.g., "Arnoxicillin" → "Amoxicillin")
- ✅ Handle multilingual text (Khmer + English + French)
- ✅ Medical terminology correction
- ✅ Structured text formatting

**Why Separate Folder?**
- Easier to fine-tune model
- Easier to replace with better model
- Cleaner deployment strategy
- Version control for models

---

### 5️⃣ AI Training (`AI/`) - Model Development

**🔬 Role**: AI model training and experimentation

**Responsibilities**:
- ✅ Train custom models for healthcare text
- ✅ Fine-tune MT5 for medical domain
- ✅ Experiment with different architectures
- ✅ Model evaluation and testing

**📌 Note**: This folder is for development only, not production deployment

---

### 6️⃣ Database (Managed by Next.js Backend)

**💾 Role**: Persistent data storage

**Stores**:
- User accounts
- Uploaded image paths
- OCR raw text output
- AI-corrected text
- User manual edits
- Confidence scores
- Review status

**Example Tables**:
- `users` - User accounts
- `prescriptions` - Uploaded prescriptions
- `ocr_results` - OCR processing results
- `reviews` - Manual review tracking

**📌 OCR backend stays stateless** - only Next.js touches the database

---

## 🔄 FULL REQUEST FLOW

```
1. User captures image → Flutter app
2. Flutter uploads → Next.js /api/ocr/upload
3. Next.js forwards image → OCR backend (Python)
4. OCR backend processes:
   ├─ Quality check (OpenCV)
   ├─ Preprocessing (deskew, denoise)
   ├─ Layout detection
   ├─ Tesseract OCR
   └─ MT5 AI correction
5. OCR backend returns → Structured JSON
6. Next.js saves result → Database
7. Next.js responds → Flutter
8. Flutter displays preview → User can edit
9. User confirms → Flutter sends to Next.js
10. Next.js marks as verified → Database
```

---

## 🧠 WHY THIS DESIGN? (Defense Strategy)

### **Question**: "Why separate services?"

**Answer**: 
> "We separate concerns for maintainability and scalability. Next.js manages user workflows, security, and data persistence, while Python handles computationally intensive OCR and AI tasks that require specialized libraries like OpenCV and PyTorch—which are not suitable for Node.js. This allows each service to use the best tools for its specific role."

### **Question**: "Why not do OCR in the mobile app?"

**Answer**:
> "Performing OCR on mobile would consume excessive battery, require large AI model downloads, and provide inconsistent results across devices. By processing on the server, we ensure consistent quality, can use more powerful models, and keep the mobile app lightweight and responsive."

### **Question**: "Why use Next.js instead of pure Node/Express?"

**Answer**:
> "Next.js provides TypeScript safety, built-in API routes, server-side rendering for admin dashboards, and excellent deployment options. It's a modern full-stack framework that reduces boilerplate while maintaining flexibility."

---

## ⚙️ DEPLOYMENT STRATEGY

| Component | Platform | Purpose |
|-----------|----------|---------|
| **Flutter App** | Play Store / APK | End-user mobile application |
| **Next.js Backend** | Vercel / VPS | API gateway and web services |
| **OCR Backend** | VPS (CPU-optimized) | Image processing and OCR |
| **MT5 Model** | Loaded at startup | Cached in memory for speed |
| **Database** | PostgreSQL (VPS/Cloud) | Data persistence |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ (for Next.js backend)
- Python 3.9+ (for OCR backend)
- Flutter 3.0+ (for mobile app)
- PostgreSQL (for database)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dastern.git
   cd dastern
   ```

2. **Setup Next.js Backend**
   ```bash
   cd backend
   npm install
   npm run dev
   ```

3. **Setup OCR Backend**
   ```bash
   cd OCR_System/ocr-backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **Setup Flutter App**
   ```bash
   cd mobile_app
   flutter pub get
   flutter run
   ```

---

## 📚 Documentation

- [AI Model Training Guide](AI/README.md)
- [OCR Backend Documentation](OCR_System/ocr-backend/README.md)
- [API Documentation](backend/README.md)

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