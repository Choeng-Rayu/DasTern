# DasTern V2 - Medical Prescription OCR & AI Assistance Platform
## Requirements Document

### 1. System Overview

**Vision**: DasTern V2 is a medical prescription digitization and assistance platform that enables patients and doctors to digitize handwritten prescriptions, understand medication instructions, track treatment history, and receive AI-assisted insights while keeping core healthcare access free and offering advanced AI intelligence at a very low cost ($0.50/month).

**Core Principles**:
- Essential healthcare features remain free
- AI-powered features available at minimal cost ($0.50/month)
- No medical diagnosis - assistance only
- Multi-language support (Khmer/English/French)
- Ethical and accessible healthcare technology

### 2. User Roles & Personas

#### 2.1 Patient (Free Tier)
**Description**: Individual users who need to digitize and manage their prescriptions
**Primary Goals**: 
- Scan and digitize prescriptions
- Set medication reminders
- View prescription history
- Understand basic medication information

#### 2.2 Patient (Premium Tier)
**Description**: Patients who want AI-powered insights and advanced features
**Primary Goals**:
- Get AI-generated medical reports
- Chat with AI assistant about medications
- Export structured reports
- Receive risk and warning alerts

#### 2.3 Doctor (Free Tier)
**Description**: Healthcare providers managing patient prescriptions
**Primary Goals**:
- View patient prescriptions
- Manage patient lists
- Add manual notes
- Track prescription history

#### 2.4 Doctor (Premium Tier)
**Description**: Healthcare providers wanting AI-assisted analysis
**Primary Goals**:
- Get AI prescription analysis
- View patient trend insights
- Generate AI-assisted clinical notes
- Priority communication with patients

#### 2.5 Admin
**Description**: System administrators
**Primary Goals**:
- Monitor system health
- Manage user accounts
- Track usage analytics

### 3. Functional Requirements

#### 3.1 Core OCR Functionality
**FR-3.1.1**: Users shall be able to capture prescription images using mobile camera
**FR-3.1.2**: System shall extract text from prescription images using OCR
**FR-3.1.3**: Users shall be able to preview raw OCR text before confirmation
**FR-3.1.4**: Users shall be able to manually edit OCR text for accuracy
**FR-3.1.5**: System shall provide confidence scores for OCR extraction

#### 3.2 Free Tier Features
**FR-3.2.1**: Free patients shall have access to basic prescription scanning
**FR-3.2.2**: Free patients shall be able to set medication reminders
**FR-3.2.3**: Free patients shall have access to last 10 scanned prescriptions
**FR-3.2.4**: Free doctors shall be able to view shared patient prescriptions
**FR-3.2.5**: Free doctors shall be able to manage basic patient lists
**FR-3.2.6**: System shall support Khmer, English, and French languages

#### 3.3 Premium Tier Features
**FR-3.3.1**: Premium patients shall receive AI-generated medical reports
**FR-3.3.2**: Premium patients shall have access to AI chat assistant for medication questions
**FR-3.3.3**: Premium patients shall get automatic OCR error correction via AI
**FR-3.3.4**: Premium patients shall have unlimited prescription history
**FR-3.3.5**: Premium patients shall be able to export reports as PDF
**FR-3.3.6**: Premium patients shall receive AI-powered risk and warning alerts
**FR-3.3.7**: Premium doctors shall get AI prescription analysis
**FR-3.3.8**: Premium doctors shall access patient trend insights
**FR-3.3.9**: Premium doctors shall have AI-assisted clinical note drafting
**FR-3.3.10**: Premium users shall have priority doctor-patient communication

#### 3.4 User Management
**FR-3.4.1**: System shall support user registration and authentication
**FR-3.4.2**: System shall manage subscription status (free/premium)
**FR-3.4.3**: System shall handle doctor-patient relationship establishment
**FR-3.4.4**: System shall validate premium features access based on subscription

#### 3.5 Data Management
**FR-3.5.1**: System shall securely store prescription data
**FR-3.5.2**: System shall maintain user interaction history
**FR-3.5.3**: System shall backup and restore user data
**FR-3.5.4**: System shall export user data in structured formats

### 4. Non-Functional Requirements

#### 4.1 Performance
**NFR-4.1.1**: OCR processing shall complete within 10 seconds
**NFR-4.1.2**: AI report generation shall complete within 30 seconds
**NFR-4.1.3**: System shall support 1000 concurrent users
**NFR-4.1.4**: Mobile app shall work offline for basic viewing

#### 4.2 Security
**NFR-4.2.1**: All medical data shall be encrypted at rest and in transit
**NFR-4.2.2**: System shall implement role-based access control
**NFR-4.2.3**: System shall log all access to medical data
**NFR-4.2.4**: System shall comply with healthcare data protection standards

#### 4.3 Usability
**NFR-4.3.1**: Mobile app shall be intuitive for non-technical users
**NFR-4.3.2**: System shall provide clear error messages
**NFR-4.3.3**: System shall support accessibility features
**NFR-4.3.4**: System shall work on Android and iOS devices

#### 4.4 Reliability
**NFR-4.4.1**: System shall have 99.5% uptime
**NFR-4.4.2**: System shall handle service failures gracefully
**NFR-4.4.3**: System shall provide data backup and recovery
**NFR-4.4.4**: System shall monitor service health automatically

### 5. Technical Architecture Requirements

#### 5.1 System Components
**TAR-5.1.1**: Flutter mobile application for user interface
**TAR-5.1.2**: Next.js backend for API and business logic
**TAR-5.1.3**: Python OCR service for text extraction
**TAR-5.1.4**: MT5 AI service for language processing
**TAR-5.1.5**: PostgreSQL database for data persistence

#### 5.2 Integration Requirements
**TAR-5.2.1**: Services shall communicate via REST APIs
**TAR-5.2.2**: System shall use Docker for containerization
**TAR-5.2.3**: System shall implement API gateway pattern
**TAR-5.2.4**: System shall use message queuing for async processing

#### 5.3 Deployment Requirements
**TAR-5.3.1**: System shall support Docker Compose development environment
**TAR-5.3.2**: System shall be deployable to cloud platforms
**TAR-5.3.3**: System shall support horizontal scaling
**TAR-5.3.4**: System shall implement CI/CD pipeline

### 6. Business Requirements

#### 6.1 Monetization
**BR-6.1.1**: Premium subscription shall cost $0.50/month
**BR-6.1.2**: System shall track subscription billing
**BR-6.1.3**: System shall provide usage analytics for business decisions
**BR-6.1.4**: System shall support payment processing integration

#### 6.2 Compliance
**BR-6.2.1**: System shall not provide medical diagnosis
**BR-6.2.2**: System shall include appropriate medical disclaimers
**BR-6.2.3**: System shall obtain user consent for data sharing
**BR-6.2.4**: System shall comply with local healthcare regulations

### 7. Acceptance Criteria

#### 7.1 Core OCR Flow
- **AC-7.1.1**: Given a prescription image, when user captures it, then OCR text is extracted within 10 seconds
- **AC-7.1.2**: Given OCR text, when user reviews it, then they can edit inaccuracies manually
- **AC-7.1.3**: Given edited text, when user confirms, then prescription is saved to their history

#### 7.2 Premium AI Features
- **AC-7.2.1**: Given a premium subscription, when user requests AI report, then structured medical report is generated
- **AC-7.2.2**: Given a premium subscription, when user asks medication question, then AI provides helpful explanation
- **AC-7.2.3**: Given OCR text with errors, when premium user processes it, then AI automatically corrects common mistakes

#### 7.3 Doctor-Patient Workflow
- **AC-7.3.1**: Given doctor invitation, when patient accepts, then doctor can view patient's prescriptions
- **AC-7.3.2**: Given shared prescriptions, when doctor reviews them, then they can add notes and insights
- **AC-7.3.3**: Given premium doctor account, when viewing patient data, then AI analysis is provided

#### 7.4 Subscription Management
- **AC-7.4.1**: Given free account, when user tries premium feature, then they are prompted to upgrade
- **AC-7.4.2**: Given premium subscription, when user accesses AI features, then they work without restrictions
- **AC-7.4.3**: Given expired subscription, when user tries premium features, then access is denied gracefully

### 8. Constraints & Assumptions

#### 8.1 Technical Constraints
- Must work on mobile devices (Android/iOS)
- Must support offline basic functionality
- Must integrate with existing OCR and AI services
- Must be deployable via Docker

#### 8.2 Business Constraints
- Premium pricing fixed at $0.50/month
- No medical diagnosis features allowed
- Must maintain free tier accessibility
- 10-week development timeline

#### 8.3 Assumptions
- Users have smartphones with cameras
- Internet connectivity available for AI features
- OCR accuracy sufficient for medical text
- AI model can handle medical terminology in multiple languages