import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { randomBytes } from 'crypto';
import { withPatientAuth } from '@/lib/middleware/auth';
import { successResponse, errorResponse } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

// POST - Create invitation code
async function handler(req: NextRequest, auth: JwtPayload) {
  try {
    const body = await req.json();
    
    const { 
      relationship_type,
      invitee_name,
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

    // Generate unique invitation code (shorter, easier to type)
    const invitationCode = `${randomBytes(3).toString('hex').toUpperCase()}`;
    
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

    // Create invitation with 'pending' status (waiting for family member to use code)
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

    // Generate QR code data
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
        invitation_code: invitationCode,
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