-- Migration: 003_family_and_reports.sql
-- Description: Family relationships, enhanced AI reports, and additional indexes
-- Created: 2026-01-23

BEGIN;

-- =============================================
-- FAMILY RELATIONSHIPS TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS family_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_member_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Relationship details
    relationship_type VARCHAR(50) NOT NULL, -- 'parent', 'child', 'spouse', 'sibling', 'caregiver', 'other'
    status relationship_status DEFAULT 'pending',
    
    -- Permissions
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

-- =============================================
-- ENHANCED AI REPORTS TABLE
-- =============================================

-- Drop existing ai_reports if we need to recreate with new structure
-- ALTER TABLE ai_reports (keep existing but add new columns)

ALTER TABLE ai_reports
    ADD COLUMN IF NOT EXISTS summary TEXT,
    ADD COLUMN IF NOT EXISTS detailed_analysis JSONB,
    ADD COLUMN IF NOT EXISTS recommendations TEXT[],
    ADD COLUMN IF NOT EXISTS warnings JSONB,
    ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en',
    ADD COLUMN IF NOT EXISTS shared_with_family BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS export_url VARCHAR(500);

-- =============================================
-- PRESCRIPTION PROCESSING QUEUE TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS prescription_processing_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    
    -- Queue status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    priority INTEGER DEFAULT 0,
    
    -- Processing details
    processing_stage VARCHAR(50), -- 'ocr', 'extraction', 'ai_analysis'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- MEDICATION SCHEDULE TEMPLATES TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS medication_schedule_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Template details
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Time slot configuration
    morning_time TIME DEFAULT '07:00',
    noon_time TIME DEFAULT '11:30',
    afternoon_time TIME DEFAULT '17:30',
    evening_time TIME DEFAULT '20:00',
    night_time TIME DEFAULT '21:00',
    
    -- Settings
    advance_notification_minutes INTEGER DEFAULT 15,
    snooze_duration_minutes INTEGER DEFAULT 10,
    
    -- Ownership
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT FALSE,
    
    -- System fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default template
INSERT INTO medication_schedule_templates (name, description, is_default)
VALUES (
    'Standard Cambodian Schedule',
    'Default time slots based on Cambodian prescription format: Morning (6-8), Noon (11-12), Afternoon (17-18), Night (20-22)',
    TRUE
) ON CONFLICT DO NOTHING;

-- =============================================
-- INDEXES FOR NEW TABLES AND COLUMNS
-- =============================================

-- Family relationships indexes
CREATE INDEX IF NOT EXISTS idx_family_patient_id ON family_relationships(patient_id);
CREATE INDEX IF NOT EXISTS idx_family_member_id ON family_relationships(family_member_id);
CREATE INDEX IF NOT EXISTS idx_family_status ON family_relationships(status);

-- Prescription processing queue indexes
CREATE INDEX IF NOT EXISTS idx_processing_queue_prescription_id ON prescription_processing_queue(prescription_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON prescription_processing_queue(status);
CREATE INDEX IF NOT EXISTS idx_processing_queue_priority ON prescription_processing_queue(priority DESC);

-- Medication reminders new indexes
CREATE INDEX IF NOT EXISTS idx_medication_reminders_prescription_id ON medication_reminders(prescription_id);
CREATE INDEX IF NOT EXISTS idx_medication_reminders_time_slot ON medication_reminders(time_slot);
CREATE INDEX IF NOT EXISTS idx_medication_reminders_next_reminder ON medication_reminders(next_reminder_at);

-- Medication reminder logs new indexes
CREATE INDEX IF NOT EXISTS idx_reminder_logs_medication_id ON medication_reminder_logs(medication_id);
CREATE INDEX IF NOT EXISTS idx_reminder_logs_patient_id ON medication_reminder_logs(patient_id);
CREATE INDEX IF NOT EXISTS idx_reminder_logs_scheduled_date ON medication_reminder_logs(scheduled_date);

-- =============================================
-- TRIGGERS FOR NEW TABLES
-- =============================================

CREATE TRIGGER update_family_relationships_updated_at 
    BEFORE UPDATE ON family_relationships 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prescription_processing_queue_updated_at 
    BEFORE UPDATE ON prescription_processing_queue 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medication_schedule_templates_updated_at 
    BEFORE UPDATE ON medication_schedule_templates 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;

