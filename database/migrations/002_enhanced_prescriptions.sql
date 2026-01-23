-- Migration: 002_enhanced_prescriptions.sql
-- Description: Enhanced prescription, medication, and reminder schema for OCR and AI processing
-- Created: 2026-01-23

BEGIN;

-- =============================================
-- NEW ENUM TYPES
-- =============================================

-- Add new prescription status values
ALTER TYPE prescription_status ADD VALUE IF NOT EXISTS 'pending';
ALTER TYPE prescription_status ADD VALUE IF NOT EXISTS 'ocr_completed';
ALTER TYPE prescription_status ADD VALUE IF NOT EXISTS 'ai_processed';

-- Create medication form type
DO $$ BEGIN
    CREATE TYPE medication_form AS ENUM (
        'tablet', 'capsule', 'syrup', 'injection', 
        'cream', 'drops', 'inhaler', 'patch', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create time slot type for dosage schedules
DO $$ BEGIN
    CREATE TYPE time_slot AS ENUM (
        'morning', 'noon', 'afternoon', 'evening', 'night'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create reminder log status type
DO $$ BEGIN
    CREATE TYPE reminder_log_status AS ENUM (
        'pending', 'taken', 'missed', 'snoozed', 'skipped'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create report type
DO $$ BEGIN
    CREATE TYPE report_type AS ENUM (
        'medical_summary', 'risk_analysis', 'trend_analysis', 
        'prescription_history', 'medication_adherence'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =============================================
-- ALTER PRESCRIPTIONS TABLE
-- =============================================

-- Add new columns to prescriptions table
ALTER TABLE prescriptions 
    ADD COLUMN IF NOT EXISTS hospital_name VARCHAR(300),
    ADD COLUMN IF NOT EXISTS hospital_address TEXT,
    ADD COLUMN IF NOT EXISTS patient_name_on_doc VARCHAR(200),
    ADD COLUMN IF NOT EXISTS patient_age INTEGER,
    ADD COLUMN IF NOT EXISTS patient_gender VARCHAR(20),
    ADD COLUMN IF NOT EXISTS diagnosis TEXT,
    ADD COLUMN IF NOT EXISTS department VARCHAR(200),
    ADD COLUMN IF NOT EXISTS prescribing_doctor_name VARCHAR(200),
    ADD COLUMN IF NOT EXISTS ocr_structured_data JSONB,
    ADD COLUMN IF NOT EXISTS error_message TEXT;

-- =============================================
-- ALTER MEDICATIONS TABLE
-- =============================================

-- Add new columns to medications table
ALTER TABLE medications
    ADD COLUMN IF NOT EXISTS sequence_number INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS quantity INTEGER,
    ADD COLUMN IF NOT EXISTS quantity_unit VARCHAR(50),
    ADD COLUMN IF NOT EXISTS duration_days INTEGER,
    ADD COLUMN IF NOT EXISTS dosage_schedule JSONB,
    ADD COLUMN IF NOT EXISTS ai_description TEXT,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Drop old form column if it's VARCHAR and recreate as enum
ALTER TABLE medications 
    ALTER COLUMN form TYPE medication_form USING form::medication_form;

-- =============================================
-- ALTER MEDICATION REMINDERS TABLE
-- =============================================

-- Add new columns to medication_reminders table
ALTER TABLE medication_reminders
    ADD COLUMN IF NOT EXISTS prescription_id UUID REFERENCES prescriptions(id) ON DELETE CASCADE,
    ADD COLUMN IF NOT EXISTS time_slot time_slot,
    ADD COLUMN IF NOT EXISTS scheduled_time TIME,
    ADD COLUMN IF NOT EXISTS dose_amount DECIMAL(10,2),
    ADD COLUMN IF NOT EXISTS dose_unit VARCHAR(50),
    ADD COLUMN IF NOT EXISTS snooze_duration_minutes INTEGER DEFAULT 10,
    ADD COLUMN IF NOT EXISTS advance_notification_minutes INTEGER DEFAULT 15,
    ADD COLUMN IF NOT EXISTS adherence_rate DECIMAL(5,2),
    ADD COLUMN IF NOT EXISTS last_taken_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS last_missed_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS next_reminder_at TIMESTAMP;

-- =============================================
-- ALTER MEDICATION REMINDER LOGS TABLE
-- =============================================

-- Add new columns to medication_reminder_logs
ALTER TABLE medication_reminder_logs
    ADD COLUMN IF NOT EXISTS medication_id UUID REFERENCES medications(id) ON DELETE CASCADE,
    ADD COLUMN IF NOT EXISTS patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ADD COLUMN IF NOT EXISTS scheduled_date DATE,
    ADD COLUMN IF NOT EXISTS dose_taken DECIMAL(10,2),
    ADD COLUMN IF NOT EXISTS skipped_reason TEXT,
    ADD COLUMN IF NOT EXISTS snoozed_until TIMESTAMP,
    ADD COLUMN IF NOT EXISTS logged_from_device VARCHAR(100);

-- Change status column to use new enum type
ALTER TABLE medication_reminder_logs 
    ALTER COLUMN status TYPE reminder_log_status USING status::reminder_log_status;

COMMIT;

