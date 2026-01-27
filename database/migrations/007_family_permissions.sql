-- Migration: 007_family_permissions.sql
-- Description: Add permissions and approval columns to family_invitations
-- Created: 2026-01-25

BEGIN;

-- Add permissions column to family_invitations
ALTER TABLE family_invitations 
ADD COLUMN IF NOT EXISTS permissions JSONB DEFAULT '{
  "can_view_prescriptions": false,
  "can_view_reminders": true,
  "can_manage_reminders": false,
  "can_receive_alerts": true
}';

-- Add QR code data column
ALTER TABLE family_invitations 
ADD COLUMN IF NOT EXISTS qr_code_data TEXT;

-- Add approval workflow columns
ALTER TABLE family_invitations 
ADD COLUMN IF NOT EXISTS requested_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS requested_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Create family_connection_requests table if not exists
CREATE TABLE IF NOT EXISTS family_connection_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invitation_id UUID NOT NULL REFERENCES family_invitations(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_member_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP,
    UNIQUE(invitation_id, family_member_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_family_invitations_permissions ON family_invitations USING GIN (permissions);
CREATE INDEX IF NOT EXISTS idx_family_invitations_status ON family_invitations(status);
CREATE INDEX IF NOT EXISTS idx_family_invitations_requested_by ON family_invitations(requested_by);
CREATE INDEX IF NOT EXISTS idx_family_requests_patient ON family_connection_requests(patient_id, status);
CREATE INDEX IF NOT EXISTS idx_family_requests_family ON family_connection_requests(family_member_id, status);

-- Add comment
COMMENT ON COLUMN family_invitations.permissions IS 'JSON object with permission flags: can_view_prescriptions, can_view_reminders, can_manage_reminders, can_receive_alerts';

COMMIT;