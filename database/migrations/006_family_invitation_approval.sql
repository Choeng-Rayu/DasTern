-- Migration: 006_family_invitation_approval.sql
-- Description: Update family invitations for approval workflow
-- Created: 2026-01-25

BEGIN;

-- Add new columns to family_invitations for approval workflow
ALTER TABLE family_invitations 
ADD COLUMN IF NOT EXISTS requested_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS requested_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Update status enum to include more states
-- Status flow: pending -> requested -> approved/rejected -> expired
COMMENT ON COLUMN family_invitations.status IS 'pending=code created, requested=family member used code, approved=patient approved, rejected=patient rejected, expired=time expired';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_family_invitations_status ON family_invitations(status);
CREATE INDEX IF NOT EXISTS idx_family_invitations_requested_by ON family_invitations(requested_by);

-- Create notifications table for approval requests (if not exists)
CREATE TABLE IF NOT EXISTS family_connection_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invitation_id UUID NOT NULL REFERENCES family_invitations(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_member_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    message TEXT, -- Optional message from family member
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP,
    UNIQUE(invitation_id, family_member_id)
);

CREATE INDEX IF NOT EXISTS idx_family_requests_patient ON family_connection_requests(patient_id, status);
CREATE INDEX IF NOT EXISTS idx_family_requests_family ON family_connection_requests(family_member_id, status);

COMMIT;