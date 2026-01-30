-- DasTern V2 Database Schema
-- Medical Prescription OCR & AI Assistance Platform
-- PostgreSQL Database Design

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE user_role AS ENUM ('patient', 'doctor', 'admin');
CREATE TYPE subscription_tier AS ENUM ('free', 'premium');
CREATE TYPE prescription_status AS ENUM ('pending', 'processing', 'ocr_completed', 'ai_processed', 'completed', 'error', 'archived');
CREATE TYPE relationship_status AS ENUM ('pending', 'active', 'inactive', 'blocked');
CREATE TYPE notification_type AS ENUM ('reminder', 'alert', 'message', 'system');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');
CREATE TYPE medication_form AS ENUM ('tablet', 'capsule', 'syrup', 'injection', 'cream', 'drops', 'inhaler', 'patch', 'other');
CREATE TYPE time_slot AS ENUM ('morning', 'noon', 'afternoon', 'evening', 'night');
CREATE TYPE reminder_log_status AS ENUM ('pending', 'taken', 'missed', 'snoozed', 'skipped');
CREATE TYPE report_type AS ENUM ('medical_summary', 'risk_analysis', 'trend_analysis', 'prescription_history', 'medication_adherence');

-- =============================================
-- CORE USER MANAGEMENT TABLES
-- =============================================

-- Users table - Core user information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'patient',
    subscription_tier subscription_tier DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    
    -- Profile information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    profile_picture_url VARCHAR(500),
    
    -- Preferences
    language_preference VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false}',
    
    -- Medical information (for patients)
    medical_conditions TEXT[],
    allergies TEXT[],
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    
    -- Professional information (for doctors)
    license_number VARCHAR(50),
    specialization VARCHAR(100),
    hospital_affiliation VARCHAR(200),
    years_of_experience INTEGER,
    
    -- System fields
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_phone CHECK (phone_number IS NULL OR phone_number ~* '^\+?[1-9]\d{1,14}$')
);

-- User sessions for JWT token management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(refresh_token)
);

-- =============================================
-- PRESCRIPTION MANAGEMENT TABLES
-- =============================================

-- Prescriptions table - Core prescription data
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Image and OCR data
    original_image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    image_metadata JSONB, -- size, format, dimensions, etc.

    -- OCR processing results
    ocr_raw_text TEXT,
    ocr_corrected_text TEXT,
    ocr_structured_data JSONB, -- Structured extraction from OCR
    ocr_confidence_score DECIMAL(5,4), -- 0.0000 to 1.0000
    ocr_language_detected VARCHAR(10),
    ocr_processing_time INTEGER, -- milliseconds

    -- AI processing results (premium feature)
    ai_report JSONB,
    ai_confidence_score DECIMAL(5,4),
    ai_processing_time INTEGER,
    ai_warnings TEXT[],

    -- Prescription metadata extracted from document
    hospital_name VARCHAR(300),
    hospital_address TEXT,
    prescription_number VARCHAR(100),
    patient_name_on_doc VARCHAR(200), -- Name as written on prescription
    patient_age INTEGER,
    patient_gender VARCHAR(20),
    diagnosis TEXT,
    department VARCHAR(200),
    prescribing_doctor_name VARCHAR(200),
    prescription_date DATE,

    -- Status and workflow
    status prescription_status DEFAULT 'pending',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,

    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_confidence_score CHECK (ocr_confidence_score IS NULL OR (ocr_confidence_score >= 0 AND ocr_confidence_score <= 1)),
    CONSTRAINT valid_ai_confidence CHECK (ai_confidence_score IS NULL OR (ai_confidence_score >= 0 AND ai_confidence_score <= 1))
);

-- Medications extracted from prescriptions
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    sequence_number INTEGER DEFAULT 1, -- Order in prescription (1, 2, 3, 4...)

    -- Medication details
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    brand_name VARCHAR(200),
    strength VARCHAR(100), -- e.g., "10mg", "100mg", "20mg"
    form medication_form DEFAULT 'tablet',

    -- Quantity and duration
    quantity INTEGER, -- Total quantity prescribed (e.g., 14, 21)
    quantity_unit VARCHAR(50), -- e.g., "គ្រាប់" (tablets), "គ្រាប់ស្រាប" (tablets+syrup)
    duration_days INTEGER, -- Treatment duration in days

    -- Dosage schedule (structured JSON matching Cambodian prescription format)
    -- Format: { morning: {dose: 1}, noon: {dose: 1}, afternoon: {dose: 1}, night: {dose: 1} }
    dosage_schedule JSONB NOT NULL DEFAULT '{}',

    -- Additional instructions
    instructions TEXT,
    take_with_food BOOLEAN DEFAULT FALSE,
    take_before_meal BOOLEAN DEFAULT FALSE,
    take_after_meal BOOLEAN DEFAULT FALSE,

    -- AI analysis (premium feature)
    ai_drug_interactions TEXT[],
    ai_side_effects TEXT[],
    ai_warnings TEXT[],
    ai_contraindications TEXT[],
    ai_description TEXT, -- AI-generated description of the medication

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Medication reminders (one per time slot per medication)
CREATE TABLE medication_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medication_id UUID NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Reminder configuration (one reminder per time slot)
    time_slot time_slot NOT NULL, -- morning, noon, afternoon, evening, night
    scheduled_time TIME NOT NULL, -- e.g., '07:00', '11:30', '17:30', '20:00'
    dose_amount DECIMAL(10,2) NOT NULL, -- How many to take at this time
    dose_unit VARCHAR(50), -- e.g., "tablet", "ml"

    -- Schedule
    days_of_week INTEGER[] DEFAULT '{1,2,3,4,5,6,7}', -- 1=Monday, 7=Sunday
    start_date DATE NOT NULL,
    end_date DATE,

    -- Reminder settings
    is_active BOOLEAN DEFAULT TRUE,
    snooze_duration_minutes INTEGER DEFAULT 10,
    advance_notification_minutes INTEGER DEFAULT 15,
    notification_sound VARCHAR(100),

    -- Tracking statistics
    total_doses INTEGER DEFAULT 0,
    completed_doses INTEGER DEFAULT 0,
    missed_doses INTEGER DEFAULT 0,
    adherence_rate DECIMAL(5,2), -- Percentage 0-100

    -- Last activity timestamps
    last_taken_at TIMESTAMP,
    last_missed_at TIMESTAMP,
    next_reminder_at TIMESTAMP,

    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Medication reminder logs (tracks each dose taken/missed/skipped)
CREATE TABLE medication_reminder_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reminder_id UUID NOT NULL REFERENCES medication_reminders(id) ON DELETE CASCADE,
    medication_id UUID NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Log details
    scheduled_date DATE NOT NULL,
    scheduled_time TIME,
    actual_time TIMESTAMP,
    status reminder_log_status NOT NULL DEFAULT 'pending',

    -- Additional info
    notes TEXT,
    dose_taken DECIMAL(10,2),
    skipped_reason TEXT,
    snoozed_until TIMESTAMP,
    logged_from_device VARCHAR(100),

    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- DOCTOR-PATIENT RELATIONSHIP TABLES
-- =============================================

-- Doctor-Patient relationships
CREATE TABLE doctor_patient_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Relationship details
    status relationship_status DEFAULT 'pending',
    invitation_code VARCHAR(50) UNIQUE,
    invitation_expires_at TIMESTAMP,
    
    -- Permissions
    can_view_prescriptions BOOLEAN DEFAULT TRUE,
    can_add_notes BOOLEAN DEFAULT TRUE,
    can_modify_reminders BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    relationship_notes TEXT,
    established_at TIMESTAMP,
    terminated_at TIMESTAMP,
    termination_reason TEXT,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique doctor-patient pairs
    UNIQUE(doctor_id, patient_id)
);

-- Family/Caregiver relationships
CREATE TABLE family_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_member_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Relationship details
    relationship_type VARCHAR(50) NOT NULL, -- 'parent', 'child', 'spouse', 'sibling', 'caregiver', 'other'
    status relationship_status DEFAULT 'pending',

    -- Permissions (what the family member can do)
    can_view_prescriptions BOOLEAN DEFAULT TRUE,
    can_view_reminders BOOLEAN DEFAULT TRUE,
    can_view_reports BOOLEAN DEFAULT FALSE,
    can_receive_alerts BOOLEAN DEFAULT TRUE,
    can_log_medications BOOLEAN DEFAULT FALSE,

    -- Invitation
    invitation_code VARCHAR(50) UNIQUE,
    invitation_expires_at TIMESTAMP,

    -- System fields
    established_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure unique relationships
    UNIQUE(patient_id, family_member_id)
);

-- Clinical notes by doctors
CREATE TABLE clinical_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prescription_id UUID REFERENCES prescriptions(id) ON DELETE SET NULL,

    -- Note content
    title VARCHAR(200),
    content TEXT NOT NULL,
    note_type VARCHAR(50), -- 'observation', 'recommendation', 'follow-up', etc.

    -- AI assistance (premium feature)
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_suggestions TEXT[],

    -- Visibility and sharing
    is_private BOOLEAN DEFAULT FALSE,
    shared_with_patient BOOLEAN DEFAULT TRUE,

    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- AI AND PREMIUM FEATURES TABLES
-- =============================================

-- AI chat conversations
CREATE TABLE ai_chat_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prescription_id UUID REFERENCES prescriptions(id) ON DELETE SET NULL,
    
    -- Conversation metadata
    title VARCHAR(200),
    context_type VARCHAR(50), -- 'prescription', 'general', 'medication'
    language VARCHAR(10) DEFAULT 'en',
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI chat messages
CREATE TABLE ai_chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES ai_chat_conversations(id) ON DELETE CASCADE,
    
    -- Message content
    message_type VARCHAR(20) NOT NULL, -- 'user', 'assistant'
    content TEXT NOT NULL,
    
    -- AI metadata
    ai_model_version VARCHAR(50),
    ai_confidence_score DECIMAL(5,4),
    ai_processing_time INTEGER, -- milliseconds
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI reports and analysis
CREATE TABLE ai_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Report type and content
    report_type report_type NOT NULL,
    summary TEXT, -- Human-readable summary
    detailed_analysis JSONB, -- Structured detailed analysis
    recommendations TEXT[], -- Array of recommendations
    warnings JSONB, -- Array of warning objects with severity

    -- AI metadata
    ai_model_version VARCHAR(50),
    ai_confidence_score DECIMAL(5,4),
    generation_time INTEGER, -- milliseconds
    language VARCHAR(10) DEFAULT 'en',

    -- Export and sharing
    exported_at TIMESTAMP,
    export_format VARCHAR(20), -- 'pdf', 'json', 'html'
    export_url VARCHAR(500),
    shared_with_doctor BOOLEAN DEFAULT FALSE,
    shared_with_family BOOLEAN DEFAULT FALSE,

    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Medication schedule templates (for default reminder times)
CREATE TABLE medication_schedule_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Template details
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Time slot configuration (default times for each slot)
    morning_time TIME DEFAULT '07:00',
    noon_time TIME DEFAULT '11:30',
    afternoon_time TIME DEFAULT '17:30',
    evening_time TIME DEFAULT '20:00',
    night_time TIME DEFAULT '21:00',

    -- Settings
    advance_notification_minutes INTEGER DEFAULT 15,
    snooze_duration_minutes INTEGER DEFAULT 10,

    -- Ownership
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL means system default
    is_default BOOLEAN DEFAULT FALSE,

    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- SUBSCRIPTION AND BILLING TABLES
-- =============================================

-- Subscription plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    tier subscription_tier NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2),
    
    -- Features
    features JSONB NOT NULL, -- list of included features
    limits JSONB, -- usage limits like max prescriptions, AI requests
    
    -- Plan status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User subscriptions
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    -- Subscription details
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'cancelled', 'expired', 'suspended'
    billing_cycle VARCHAR(20) NOT NULL, -- 'monthly', 'yearly'
    
    -- Billing dates
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    trial_end TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Payment information
    payment_method_id VARCHAR(100), -- Stripe payment method ID
    last_payment_at TIMESTAMP,
    next_billing_date TIMESTAMP,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payment transactions
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES user_subscriptions(id) ON DELETE SET NULL,
    
    -- Transaction details
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    
    -- Payment gateway information
    payment_gateway VARCHAR(50), -- 'stripe', 'paypal', etc.
    gateway_transaction_id VARCHAR(200),
    gateway_response JSONB,
    
    -- Transaction status
    status payment_status DEFAULT 'pending',
    processed_at TIMESTAMP,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- SYSTEM AND ANALYTICS TABLES
-- =============================================

-- System notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification content
    type notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Notification metadata
    data JSONB, -- additional data for the notification
    action_url VARCHAR(500), -- deep link or URL to open
    
    -- Delivery status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    sent_at TIMESTAMP,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Usage analytics
CREATE TABLE usage_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL, -- 'prescription_scan', 'ai_report_generated', etc.
    event_data JSONB,
    
    -- Session information
    session_id VARCHAR(100),
    device_type VARCHAR(50),
    platform VARCHAR(50), -- 'ios', 'android', 'web'
    app_version VARCHAR(20),
    
    -- Location (if available)
    ip_address INET,
    country VARCHAR(2),
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW()
);

-- System audit logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Audit details
    action VARCHAR(100) NOT NULL, -- 'create', 'update', 'delete', 'view'
    resource_type VARCHAR(50) NOT NULL, -- 'prescription', 'user', 'subscription'
    resource_id UUID,
    
    -- Change details
    old_values JSONB,
    new_values JSONB,
    
    -- Request metadata
    ip_address INET,
    user_agent TEXT,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX idx_users_created_at ON users(created_at);

-- User sessions indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Prescriptions table indexes
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_doctor_id ON prescriptions(doctor_id);
CREATE INDEX idx_prescriptions_status ON prescriptions(status);
CREATE INDEX idx_prescriptions_created_at ON prescriptions(created_at);
CREATE INDEX idx_prescriptions_prescription_date ON prescriptions(prescription_date);

-- Medications table indexes
CREATE INDEX idx_medications_prescription_id ON medications(prescription_id);
CREATE INDEX idx_medications_name ON medications(name);
CREATE INDEX idx_medications_is_active ON medications(is_active);
CREATE INDEX idx_medications_sequence ON medications(prescription_id, sequence_number);

-- Medication reminders indexes
CREATE INDEX idx_medication_reminders_patient_id ON medication_reminders(patient_id);
CREATE INDEX idx_medication_reminders_medication_id ON medication_reminders(medication_id);
CREATE INDEX idx_medication_reminders_prescription_id ON medication_reminders(prescription_id);
CREATE INDEX idx_medication_reminders_is_active ON medication_reminders(is_active);
CREATE INDEX idx_medication_reminders_time_slot ON medication_reminders(time_slot);
CREATE INDEX idx_medication_reminders_scheduled_time ON medication_reminders(scheduled_time);
CREATE INDEX idx_medication_reminders_start_date ON medication_reminders(start_date);
CREATE INDEX idx_medication_reminders_next_reminder ON medication_reminders(next_reminder_at);

-- Medication reminder logs indexes
CREATE INDEX idx_reminder_logs_reminder_id ON medication_reminder_logs(reminder_id);
CREATE INDEX idx_reminder_logs_medication_id ON medication_reminder_logs(medication_id);
CREATE INDEX idx_reminder_logs_patient_id ON medication_reminder_logs(patient_id);
CREATE INDEX idx_reminder_logs_scheduled_date ON medication_reminder_logs(scheduled_date);
CREATE INDEX idx_reminder_logs_status ON medication_reminder_logs(status);

-- Doctor-patient relationships indexes
CREATE INDEX idx_doctor_patient_doctor_id ON doctor_patient_relationships(doctor_id);
CREATE INDEX idx_doctor_patient_patient_id ON doctor_patient_relationships(patient_id);
CREATE INDEX idx_doctor_patient_status ON doctor_patient_relationships(status);

-- Family relationships indexes
CREATE INDEX idx_family_patient_id ON family_relationships(patient_id);
CREATE INDEX idx_family_member_id ON family_relationships(family_member_id);
CREATE INDEX idx_family_status ON family_relationships(status);

-- Clinical notes indexes
CREATE INDEX idx_clinical_notes_doctor_id ON clinical_notes(doctor_id);
CREATE INDEX idx_clinical_notes_patient_id ON clinical_notes(patient_id);
CREATE INDEX idx_clinical_notes_prescription_id ON clinical_notes(prescription_id);

-- AI chat indexes
CREATE INDEX idx_ai_chat_conversations_user_id ON ai_chat_conversations(user_id);
CREATE INDEX idx_ai_chat_messages_conversation_id ON ai_chat_messages(conversation_id);

-- Subscription indexes
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_user_subscriptions_current_period_end ON user_subscriptions(current_period_end);

-- Analytics indexes
CREATE INDEX idx_usage_analytics_user_id ON usage_analytics(user_id);
CREATE INDEX idx_usage_analytics_event_type ON usage_analytics(event_type);
CREATE INDEX idx_usage_analytics_created_at ON usage_analytics(created_at);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_type ON notifications(type);

-- =============================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medication_reminders_updated_at BEFORE UPDATE ON medication_reminders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_doctor_patient_relationships_updated_at BEFORE UPDATE ON doctor_patient_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_family_relationships_updated_at BEFORE UPDATE ON family_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clinical_notes_updated_at BEFORE UPDATE ON clinical_notes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_chat_conversations_updated_at BEFORE UPDATE ON ai_chat_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_reports_updated_at BEFORE UPDATE ON ai_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medication_schedule_templates_updated_at BEFORE UPDATE ON medication_schedule_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscription_plans_updated_at BEFORE UPDATE ON subscription_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_transactions_updated_at BEFORE UPDATE ON payment_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- View for user profile with subscription info
CREATE VIEW user_profiles AS
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    u.subscription_tier,
    u.language_preference,
    u.profile_picture_url,
    u.is_active,
    u.created_at,
    us.status as subscription_status,
    us.current_period_end as subscription_expires_at,
    sp.name as plan_name
FROM users u
LEFT JOIN user_subscriptions us ON u.id = us.user_id AND us.status = 'active'
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id;

-- View for prescription summary with medication count
CREATE VIEW prescription_summaries AS
SELECT 
    p.id,
    p.patient_id,
    p.doctor_id,
    p.status,
    p.prescription_date,
    p.ocr_confidence_score,
    p.created_at,
    COUNT(m.id) as medication_count,
    u_patient.first_name || ' ' || u_patient.last_name as patient_name,
    u_doctor.first_name || ' ' || u_doctor.last_name as doctor_name
FROM prescriptions p
LEFT JOIN medications m ON p.id = m.prescription_id
LEFT JOIN users u_patient ON p.patient_id = u_patient.id
LEFT JOIN users u_doctor ON p.doctor_id = u_doctor.id
GROUP BY p.id, u_patient.first_name, u_patient.last_name, u_doctor.first_name, u_doctor.last_name;

-- View for active doctor-patient relationships
CREATE VIEW active_doctor_patient_relationships AS
SELECT
    dpr.id,
    dpr.doctor_id,
    dpr.patient_id,
    dpr.established_at,
    u_doctor.first_name || ' ' || u_doctor.last_name as doctor_name,
    u_doctor.specialization,
    u_patient.first_name || ' ' || u_patient.last_name as patient_name,
    u_patient.email as patient_email
FROM doctor_patient_relationships dpr
JOIN users u_doctor ON dpr.doctor_id = u_doctor.id
JOIN users u_patient ON dpr.patient_id = u_patient.id
WHERE dpr.status = 'active';

-- View for today's medication reminders
CREATE VIEW todays_reminders AS
SELECT
    mr.id as reminder_id,
    mr.medication_id,
    mr.prescription_id,
    mr.patient_id,
    m.name as medication_name,
    m.strength as medication_strength,
    m.form as medication_form,
    mr.time_slot,
    mr.scheduled_time,
    mr.dose_amount,
    mr.dose_unit,
    mr.adherence_rate,
    p.hospital_name,
    p.diagnosis
FROM medication_reminders mr
JOIN medications m ON mr.medication_id = m.id
JOIN prescriptions p ON mr.prescription_id = p.id
WHERE mr.is_active = TRUE
  AND EXTRACT(DOW FROM CURRENT_DATE) = ANY(
      CASE WHEN EXTRACT(DOW FROM CURRENT_DATE) = 0 THEN ARRAY[7]
           ELSE ARRAY[EXTRACT(DOW FROM CURRENT_DATE)::INTEGER] END
  )
  AND (mr.start_date <= CURRENT_DATE)
  AND (mr.end_date IS NULL OR mr.end_date >= CURRENT_DATE);

-- View for patient adherence summary
CREATE VIEW patient_adherence_summary AS
SELECT
    mr.patient_id,
    u.first_name || ' ' || u.last_name as patient_name,
    COUNT(DISTINCT mr.id) as active_reminders,
    SUM(mr.total_doses) as total_doses,
    SUM(mr.completed_doses) as completed_doses,
    SUM(mr.missed_doses) as missed_doses,
    CASE
        WHEN SUM(mr.total_doses) > 0
        THEN ROUND(SUM(mr.completed_doses)::DECIMAL / SUM(mr.total_doses) * 100, 2)
        ELSE 0
    END as overall_adherence_rate
FROM medication_reminders mr
JOIN users u ON mr.patient_id = u.id
WHERE mr.is_active = TRUE
GROUP BY mr.patient_id, u.first_name, u.last_name;

-- =============================================
-- INITIAL DATA SETUP
-- =============================================

-- Insert default medication schedule template
INSERT INTO medication_schedule_templates (name, description, is_default)
VALUES (
    'Cambodian Standard Schedule',
    'Default time slots based on Cambodian prescription format: Morning (6-8 AM), Noon (11-12 PM), Afternoon (5-6 PM), Night (8-10 PM)',
    TRUE
);

-- Insert default subscription plans
INSERT INTO subscription_plans (name, tier, price_monthly, price_yearly, features, limits) VALUES
('Free Plan', 'free', 0.00, 0.00, 
 '["prescription_scan", "ocr_extraction", "manual_edit", "medication_reminders", "basic_history"]',
 '{"max_prescriptions": 10, "ai_requests": 0}'),
('Premium Plan', 'premium', 0.50, 5.00,
 '["prescription_scan", "ocr_extraction", "manual_edit", "medication_reminders", "unlimited_history", "ai_reports", "ai_chat", "ocr_correction", "pdf_export", "risk_alerts"]',
 '{"max_prescriptions": -1, "ai_requests": 1000}');

-- Create admin user (password should be changed in production)
INSERT INTO users (email, password_hash, role, first_name, last_name, is_active, email_verified) VALUES
('admin@dastern.com', crypt('admin123', gen_salt('bf')), 'admin', 'System', 'Administrator', true, true);

-- =============================================
-- SECURITY POLICIES (Row Level Security)
-- =============================================

-- Enable RLS on sensitive tables
ALTER TABLE prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE clinical_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_messages ENABLE ROW LEVEL SECURITY;

-- Prescription access policy
CREATE POLICY prescription_access_policy ON prescriptions
    FOR ALL
    TO authenticated_users
    USING (
        patient_id = current_user_id() OR 
        doctor_id = current_user_id() OR
        EXISTS (
            SELECT 1 FROM doctor_patient_relationships dpr 
            WHERE dpr.patient_id = prescriptions.patient_id 
            AND dpr.doctor_id = current_user_id() 
            AND dpr.status = 'active'
        )
    );

-- Note: current_user_id() function would need to be implemented based on your authentication system