# DasTern V2 - System Design Document

## 1. Architecture Overview

### 1.1 System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │  Next.js API    │    │   PostgreSQL    │
│  (Presentation) │◄──►│  (Controller)   │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼────────┐  ┌──────▼────────┐
            │  OCR Service   │  │  AI Service(ollama)   │
            │   (Python)     │  │    (llama)      │
            └────────────────┘  └───────────────┘
```   

### 1.2 Service Responsibilities

#### Flutter Mobile App
- User interface and experience
- Camera integration for image capture
- Offline data viewing
- Push notifications for reminders
- Local data caching
  
#### Next.js Backend (Control Tower)
- Authentication and authorization
- Subscription management and validation
- API gateway and request routing
- Business logic orchestration
- Data persistence coordination
- Rate limiting and security

#### OCR Service (Python)
- Image preprocessing and enhancement
- Text extraction using Tesseract/PaddleOCR
- Confidence scoring
- Language detection
- Output formatting

#### AI LLM Service (MT5)
- Text correction and normalization
- Medical terminology understanding
- Report generation
- Chat assistance
- Risk assessment (non-diagnostic)

#### PostgreSQL Database
- User accounts and profiles
- Prescription data and history
- Subscription information
- Doctor-patient relationships
- System logs and analytics

## 2. Data Models

### 2.1 Core Entities

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL,
    subscription_tier ENUM('free', 'premium') DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Prescriptions table
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES users(id),
    doctor_id UUID REFERENCES users(id),
    original_image_url VARCHAR(500),
    ocr_raw_text TEXT,
    ocr_corrected_text TEXT,
    ocr_confidence_score DECIMAL(3,2),
    ai_report JSONB,
    status ENUM('processing', 'completed', 'error') DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Doctor-Patient relationships
CREATE TABLE doctor_patient_relationships (
    id UUID PRIMARY KEY,
    doctor_id UUID REFERENCES users(id),
    patient_id UUID REFERENCES users(id),
    status ENUM('pending', 'active', 'inactive') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(doctor_id, patient_id)
);

-- Medication reminders
CREATE TABLE medication_reminders (
    id UUID PRIMARY KEY,
    prescription_id UUID REFERENCES prescriptions(id),
    patient_id UUID REFERENCES users(id),
    medication_name VARCHAR(255),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    reminder_times TIME[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI chat history
CREATE TABLE ai_chat_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    prescription_id UUID REFERENCES prescriptions(id),
    question TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 API Schemas

#### Prescription Processing Request
```json
{
  "image": "base64_encoded_image",
  "language": "en|km|fr",
  "enhance_with_ai": boolean
}
```

#### AI Report Response
```json
{
  "prescription_id": "uuid",
  "medications": [
    {
      "name": "string",
      "dosage": "string",
      "frequency": "string",
      "duration": "string",
      "instructions": "string"
    }
  ],
  "warnings": ["string"],
  "summary": "string",
  "confidence": 0.95
}
```

## 3. Feature Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Establish core infrastructure and basic user management

#### Week 1: Infrastructure Setup
- Set up Docker development environment
- Configure PostgreSQL database with initial schema
- Create Next.js API structure with authentication
- Set up Flutter project with basic navigation
- Implement user registration and login

#### Week 2: Basic User Management
- Complete authentication flow (JWT tokens)
- Implement user profiles and settings
- Add language preference selection
- Create basic subscription status tracking
- Set up error handling and logging

### Phase 2: Core OCR Functionality (Weeks 3-4)
**Goal**: Implement basic prescription scanning and text extraction

#### Week 3: Image Capture & OCR Service
- Implement camera integration in Flutter
- Create OCR service with Tesseract/PaddleOCR
- Add image preprocessing pipeline
- Implement basic text extraction
- Create OCR confidence scoring

#### Week 4: OCR Integration & Preview
- Connect Flutter app to OCR service via Next.js API
- Implement OCR text preview and manual editing
- Add prescription data storage
- Create basic prescription history view
- Implement free tier limitations (10 prescriptions)

### Phase 3: Free Tier Features (Weeks 5-6)
**Goal**: Complete all free tier functionality

#### Week 5: Medication Management
- Implement medication reminder system
- Add prescription history management
- Create basic prescription sharing between doctor-patient
- Implement multi-language support (Khmer/English/French)
- Add offline viewing capabilities

#### Week 6: Doctor Features & Polish
- Implement doctor-patient relationship management
- Add doctor's prescription review interface
- Create manual note-taking for doctors
- Implement basic patient list management
- Polish UI/UX for free tier features

### Phase 4: AI Service Integration (Weeks 7-8)
**Goal**: Implement AI-powered features for premium tier

#### Week 7: AI Service Setup
- Set up MT5 model service
- Implement OCR text correction using AI
- Create AI medical report generation
- Add AI chat assistant basic functionality
- Implement subscription validation middleware

#### Week 8: Premium AI Features
- Complete AI medical report with structured output
- Implement AI chat assistant with context awareness
- Add risk and warning alert generation
- Create AI-assisted clinical notes for doctors
- Implement patient trend analysis

### Phase 5: Premium Features & Business Logic (Week 9)
**Goal**: Complete premium tier and subscription management

#### Week 9: Subscription & Premium Features
- Implement subscription upgrade/downgrade flow
- Add payment processing integration
- Create premium feature access controls
- Implement unlimited history for premium users
- Add PDF export functionality
- Create priority doctor-patient communication

### Phase 6: Testing, Optimization & Deployment (Week 10)
**Goal**: Finalize system with testing and deployment

#### Week 10: Final Integration & Deployment
- Comprehensive testing (unit, integration, E2E)
- Performance optimization and caching
- Security audit and penetration testing
- Production deployment setup
- Documentation and user guides
- System monitoring and analytics setup

## 4. Technical Specifications

### 4.1 API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

#### Prescriptions
- `POST /api/prescriptions` - Upload and process prescription
- `GET /api/prescriptions` - Get user's prescriptions
- `GET /api/prescriptions/:id` - Get specific prescription
- `PUT /api/prescriptions/:id` - Update prescription
- `DELETE /api/prescriptions/:id` - Delete prescription

#### AI Features (Premium)
- `POST /api/ai/report/:prescriptionId` - Generate AI report
- `POST /api/ai/chat` - AI chat assistant
- `POST /api/ai/correct-ocr` - AI OCR correction

#### Doctor Features
- `GET /api/doctor/patients` - Get doctor's patients
- `POST /api/doctor/invite` - Invite patient
- `GET /api/doctor/prescriptions/:patientId` - Get patient prescriptions
- `POST /api/doctor/notes` - Add clinical notes

#### Subscriptions
- `GET /api/subscription/status` - Get subscription status
- `POST /api/subscription/upgrade` - Upgrade to premium
- `POST /api/subscription/cancel` - Cancel subscription

### 4.2 Security Measures

#### Authentication & Authorization
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- API rate limiting per user/IP
- Input validation and sanitization

#### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Medical data anonymization
- Secure file storage with signed URLs

#### Privacy & Compliance
- User consent management
- Data retention policies
- Audit logging for medical data access
- GDPR compliance features

### 4.3 Performance Optimization

#### Caching Strategy
- Redis for session management
- CDN for static assets
- Database query optimization
- API response caching

#### Scalability
- Horizontal scaling for API services
- Load balancing for high availability
- Database connection pooling
- Async processing for heavy operations

## 5. Deployment Architecture

### 5.1 Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  nextjs:
    build: ./backend-nextjs
    ports: ["3000:3000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/dastern
      - OCR_SERVICE_URL=http://ocr-service:8000
      - AI_SERVICE_URL=http://ai-service:8001
  
  ocr-service:
    build: ./ocr-service
    ports: ["8000:8000"]
  
  ai-service:
    build: ./ai-llm-service
    ports: ["8001:8001"]
  
  postgres:
    image: postgres:15
    ports: ["5432:5432"]
    environment:
      - POSTGRES_DB=dastern
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

### 5.2 Production Deployment
- Container orchestration (Kubernetes/Docker Swarm)
- Load balancers for high availability
- Database clustering and replication
- Monitoring and alerting (Prometheus/Grafana)
- Automated backups and disaster recovery

## 6. Quality Assurance

### 6.1 Testing Strategy
- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Performance testing for OCR and AI services
- Security testing for authentication and data protection

### 6.2 Monitoring & Analytics
- Application performance monitoring (APM)
- Error tracking and alerting
- User behavior analytics
- System health dashboards
- Business metrics tracking

## 7. Success Metrics

### 7.1 Technical Metrics
- OCR accuracy > 90%
- API response time < 2 seconds
- System uptime > 99.5%
- Mobile app crash rate < 1%

### 7.2 Business Metrics
- User registration and retention rates
- Premium subscription conversion rate
- Feature usage analytics
- Customer satisfaction scores

This design provides a comprehensive roadmap for implementing DasTern V2 over 10 weeks, with clear phases, technical specifications, and success criteria.