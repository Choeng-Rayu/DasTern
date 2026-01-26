-- Migration: 005_role_profiles.sql
-- Description: Add role-specific profile tables and update onboarding flow
-- Created: 2026-01-24

BEGIN;

-- =============================================
-- DROP existing enum if it exists (for clean migration)
-- =============================================
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'onboarding_status') THEN
        -- Update existing columns to text temporarily
        ALTER TABLE users ALTER COLUMN onboarding_status DROP DEFAULT;
        ALTER TABLE users ALTER COLUMN onboarding_status TYPE VARCHAR(30);
        DROP TYPE onboarding_status;
    END IF;
END $$;

-- =============================================
-- Create onboarding status enum
-- =============================================
CREATE TYPE onboarding_status AS ENUM (
    'pending',           -- Just registered, no role selected
    'role_selected',     -- Role selected, profile incomplete
    'profile_pending',   -- Profile submitted, awaiting verification (doctors only)
    'active'             -- Fully onboarded and verified
);

-- =============================================
-- Update users table
-- =============================================
ALTER TABLE users 
    ALTER COLUMN onboarding_status TYPE onboarding_status USING onboarding_status::onboarding_status,
    ALTER COLUMN onboarding_status SET DEFAULT 'pending';

-- Add columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role_selected_at') THEN
        ALTER TABLE users ADD COLUMN role_selected_at TIMESTAMP;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'profile_completed_at') THEN
        ALTER TABLE users ADD COLUMN profile_completed_at TIMESTAMP;
    END IF;
END $$;

-- =============================================
-- PATIENT PROFILES TABLE
-- Stores patient-specific medical and preference data
-- =============================================
CREATE TABLE IF NOT EXISTS patient_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Meal schedule preferences (for medication timing)
    meal_schedule JSONB NOT NULL DEFAULT '{
        "morning": "07:00",
        "noon": "12:00", 
        "evening": "18:00",
        "night": "21:00"
    }',
    use_custom_schedule BOOLEAN DEFAULT FALSE,
    
    -- Emergency contact
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    
    -- Medical information
    blood_type VARCHAR(5),
    medical_conditions TEXT[] DEFAULT '{}',
    allergies TEXT[] DEFAULT '{}',
    current_medications TEXT[] DEFAULT '{}',
    
    -- Insurance (optional)
    insurance_provider VARCHAR(100),
    insurance_policy_number VARCHAR(50),
    
    -- Preferences
    reminder_advance_minutes INTEGER DEFAULT 15,
    preferred_pharmacy VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patient_profiles_user_id ON patient_profiles(user_id);

-- =============================================
-- DOCTOR PROFILES TABLE
-- Stores doctor-specific professional data
-- =============================================
CREATE TABLE IF NOT EXISTS doctor_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Professional information
    license_number VARCHAR(50) NOT NULL,
    license_expiry_date DATE,
    specialization VARCHAR(100) NOT NULL,
    sub_specializations TEXT[] DEFAULT '{}',
    
    -- Workplace
    hospital_name VARCHAR(200) NOT NULL,
    hospital_address TEXT,
    clinic_name VARCHAR(200),
    clinic_address TEXT,
    
    -- Experience
    years_of_experience INTEGER NOT NULL,
    medical_school VARCHAR(200),
    graduation_year INTEGER,
    
    -- Verification
    verification_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    verification_documents JSONB DEFAULT '[]',
    verified_at TIMESTAMP,
    verified_by UUID REFERENCES users(id),
    rejection_reason TEXT,
    
    -- Availability
    consultation_fee DECIMAL(10,2),
    available_for_consultation BOOLEAN DEFAULT TRUE,
    consultation_hours JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_user_id ON doctor_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_license ON doctor_profiles(license_number);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_verification ON doctor_profiles(verification_status);

-- =============================================
-- FAMILY MEMBER PROFILES TABLE
-- Stores family member relationship data
-- =============================================
CREATE TABLE IF NOT EXISTS family_member_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- This is filled after linking with patient
    linked_patient_id UUID REFERENCES users(id) ON DELETE SET NULL,
    relationship_type VARCHAR(50), -- parent, child, spouse, sibling, guardian, other
    
    -- Permissions granted by patient
    can_view_prescriptions BOOLEAN DEFAULT FALSE,
    can_view_reminders BOOLEAN DEFAULT TRUE,
    can_manage_reminders BOOLEAN DEFAULT FALSE,
    can_receive_alerts BOOLEAN DEFAULT TRUE,
    
    -- Notification preferences
    alert_on_missed_medication BOOLEAN DEFAULT TRUE,
    alert_on_low_stock BOOLEAN DEFAULT FALSE,
    
    linked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_family_profiles_user_id ON family_member_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_family_profiles_patient_id ON family_member_profiles(linked_patient_id);

-- =============================================
-- FAMILY INVITATIONS TABLE
-- For QR code / invitation code linking
-- =============================================
CREATE TABLE IF NOT EXISTS family_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Who sent the invitation (patient)
    inviter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Invitation details
    invitation_code VARCHAR(20) UNIQUE NOT NULL,
    qr_code_data TEXT, -- Base64 or URL for QR
    
    -- Who is invited
    invitee_email VARCHAR(255),
    invitee_phone VARCHAR(20),
    relationship_type VARCHAR(50) NOT NULL,
    
    -- Permissions to grant
    permissions JSONB DEFAULT '{
        "can_view_prescriptions": false,
        "can_view_reminders": true,
        "can_manage_reminders": false,
        "can_receive_alerts": true
    }',
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, expired, revoked
    expires_at TIMESTAMP NOT NULL,
    
    -- When accepted
    accepted_at TIMESTAMP,
    accepted_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_family_invitations_code ON family_invitations(invitation_code);
CREATE INDEX IF NOT EXISTS idx_family_invitations_inviter ON family_invitations(inviter_id);
CREATE INDEX IF NOT EXISTS idx_family_invitations_status ON family_invitations(status);

-- =============================================
-- USER SESSIONS TABLE
-- For JWT refresh token management
-- =============================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(refresh_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active, expires_at);

-- =============================================
-- AUDIT LOGS TABLE
-- For security and compliance
-- =============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    action VARCHAR(100) NOT NULL, -- login, logout, profile_update, etc.
    resource_type VARCHAR(50), -- user, prescription, reminder, etc.
    resource_id UUID,
    
    old_values JSONB,
    new_values JSONB,
    
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);

-- =============================================
-- FUNCTIONS
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS update_patient_profiles_updated_at ON patient_profiles;
CREATE TRIGGER update_patient_profiles_updated_at
    BEFORE UPDATE ON patient_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_doctor_profiles_updated_at ON doctor_profiles;
CREATE TRIGGER update_doctor_profiles_updated_at
    BEFORE UPDATE ON doctor_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_family_profiles_updated_at ON family_member_profiles;
CREATE TRIGGER update_family_profiles_updated_at
    BEFORE UPDATE ON family_member_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;