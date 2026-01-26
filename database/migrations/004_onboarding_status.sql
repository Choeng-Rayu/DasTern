-- Migration: 0004_role_user.sql
-- description: role selected
-- created: 23/01/26

BEGIN;

-- Add onboarding status enum
CREATE TYPE onboarding_status AS ENUM (
    'pending',           -- Just registered, no role selected
    'role_selected',     -- Role selected, profile incomplete
    'profile_pending',   -- Profile submitted, awaiting verification (doctors)
    'verified',          -- Email/phone verified
    'active'             -- Fully onboarded
);

-- Add onboarding columns to users table
ALTER TABLE users 
ADD COLUMN onboarding_status onboarding_status DEFAULT 'pending',
ADD COLUMN role_selected_at TIMESTAMP,
ADD COLUMN profile_completed_at TIMESTAMP,
ADD COLUMN verification_code VARCHAR(6),
ADD COLUMN verification_code_expires_at TIMESTAMP,
ADD COLUMN doctor_verification_status VARCHAR(20) DEFAULT NULL,
ADD COLUMN doctor_verification_documents JSONB DEFAULT NULL;

-- Create index for onboarding queries
CREATE INDEX idx_users_onboarding_status ON users(onboarding_status);

-- Add family member invitation tracking
CREATE TABLE family_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inviter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitee_phone VARCHAR(20),
    invitee_email VARCHAR(255),
    invitation_code VARCHAR(50) UNIQUE NOT NULL,
    qr_code_data TEXT,
    relationship_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    accepted_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_family_invitations_code ON family_invitations(invitation_code);
CREATE INDEX idx_family_invitations_inviter ON family_invitations(inviter_id);

COMMIT;