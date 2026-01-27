import { ValidationResult } from './auth.validator';
import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { randomBytes } from 'crypto';
import { withPatientAuth } from '@/lib/middleware/auth';
import { successResponse, errorResponse } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

// Generate easy-to-read invitation code
function generateInvitationCode(): string {
  // Exclude confusing characters: 0/O, 1/I/L
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
  const bytes = randomBytes(6);
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars[bytes[i] % chars.length];
  }
  return code;
}

// POST - Create invitation code
async function handler(req: NextRequest, auth: JwtPayload) {
  try {
    const body = await req.json();
    
    const { 
      relationship_type,
      permissions
    } = body;

    // Validate
    if (!relationship_type) {
      return errorResponse('Relationship type is required', 400);
    }

    const validRelationships = ['spouse', 'parent', 'child', 'sibling', 'guardian', 'caregiver', 'other'];
    if (!validRelationships.includes(relationship_type)) {
      return errorResponse(`Invalid relationship. Must be: ${validRelationships.join(', ')}`, 400);
    }

    // Generate unique invitation code (auto-generated, not manual)
    let invitationCode = generateInvitationCode();
    
    // Ensure code is unique
    let attempts = 0;
    while (attempts < 5) {
      const existing = await query(
        'SELECT id FROM family_invitations WHERE invitation_code = $1',
        [invitationCode]
      );
      if (existing.rowCount === 0) break;
      invitationCode = generateInvitationCode();
      attempts++;
    }
    
    // Set expiration (7 days from now)
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    // Default permissions
    const defaultPermissions = {
      can_view_prescriptions: false,
      can_view_reminders: true,
      can_manage_reminders: false,
      can_receive_alerts: true
    };

    const finalPermissions = { ...defaultPermissions, ...permissions };

    // Create invitation with 'pending' status
    const result = await query(
      `INSERT INTO family_invitations (
        inviter_id, invitation_code, relationship_type,
        permissions, expires_at, status
      ) VALUES ($1, $2, $3, $4, $5, 'pending')
      RETURNING id, invitation_code, relationship_type, expires_at, permissions`,
      [
        auth.userId,
        invitationCode,
        relationship_type,
        JSON.stringify(finalPermissions),
        expiresAt
      ]
    );

    const invitation = result.rows[0];

    // Generate QR code data (Flutter app will render QR from this)
    const qrCodeData = JSON.stringify({
      type: 'dastern_family_invite',
      code: invitationCode,
      expires: expiresAt.toISOString()
    });

    // Update with QR data
    await query(
      'UPDATE family_invitations SET qr_code_data = $1 WHERE id = $2',
      [qrCodeData, invitation.id]
    );

    return successResponse(
      {
        invitation_id: invitation.id,
        invitation_code: invitationCode,  // Auto-generated code
        qr_code_data: qrCodeData,
        relationship_type: relationship_type,
        permissions: finalPermissions,
        expires_at: expiresAt.toISOString(),
        status: 'pending',
        share_message: `Connect with me on DasTern! Use code: ${invitationCode}`
      },
      'Invitation created successfully'
    );

  } catch (error) {
    console.error('Create invitation error:', error);
    return errorResponse('Failed to create invitation', 500);
  }
}

// GET - Get all invitations and pending requests
async function getHandler(req: NextRequest, auth: JwtPayload) {
  try {
    // Get all invitations created by patient
    const invitationsResult = await query(
      `SELECT 
        fi.id, fi.invitation_code, fi.relationship_type, fi.status,
        fi.qr_code_data, fi.expires_at, fi.created_at, fi.permissions,
        fi.approved_at, fi.rejected_at,
        u.id as requester_id,
        u.first_name as requester_first_name,
        u.last_name as requester_last_name,
        u.email as requester_email
      FROM family_invitations fi
      LEFT JOIN users u ON fi.requested_by = u.id
      WHERE fi.inviter_id = $1
      ORDER BY fi.created_at DESC`,
      [auth.userId]
    );

    // Get pending connection requests
    const requestsResult = await query(
      `SELECT 
        fcr.id, fcr.status, fcr.message, fcr.created_at,
        fi.invitation_code, fi.relationship_type, fi.permissions,
        u.id as family_member_id,
        u.first_name, u.last_name, u.email, u.phone_number
      FROM family_connection_requests fcr
      JOIN family_invitations fi ON fcr.invitation_id = fi.id
      JOIN users u ON fcr.family_member_id = u.id
      WHERE fcr.patient_id = $1 AND fcr.status = 'pending'
      ORDER BY fcr.created_at DESC`,
      [auth.userId]
    );

    return successResponse({
      invitations: invitationsResult.rows.map(inv => ({
        ...inv,
        is_expired: new Date(inv.expires_at) < new Date(),
        permissions: inv.permissions
      })),
      pending_requests: requestsResult.rows
    });

  } catch (error) {
    console.error('Get invitations error:', error);
    return errorResponse('Failed to get invitations', 500);
  }
}

export const POST = withPatientAuth(handler);
export const GET = withPatientAuth(getHandler);

export function validateFamilyProfile(data: any): ValidationResult {
  const errors: Record<string, string> = {};

  // No required fields for family member profile completion
  // They just need to complete basic onboarding, then connect with patient
  
  // Optional: validate preferred_relationship if provided
  if (data.preferred_relationship) {
    const validRelationships = ['spouse', 'parent', 'child', 'sibling', 'guardian', 'caregiver', 'other'];
    if (!validRelationships.includes(data.preferred_relationship)) {
      errors.preferred_relationship = `Invalid relationship. Must be: ${validRelationships.join(', ')}`;
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}

export function validateInvitationCode(data: any): ValidationResult {
  const errors: Record<string, string> = {};

  if (!data.invitation_code) {
    errors.invitation_code = 'Invitation code is required';
  } else if (data.invitation_code.length < 6) {
    errors.invitation_code = 'Invalid invitation code format';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}