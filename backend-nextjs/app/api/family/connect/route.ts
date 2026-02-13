import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { withFamilyAuth } from '@/lib/middleware/auth';
import { successResponse, errorResponse } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

// POST - Family member uses invitation code to request connection
async function handler(req: NextRequest, auth: JwtPayload) {
  try {
    const body = await req.json();
    const { invitation_code, message } = body;

    if (!invitation_code) {
      return errorResponse('Invitation code is required', 400);
    }

    // Find the invitation
    const invitationResult = await query(
      `SELECT 
        fi.id, fi.inviter_id, fi.relationship_type, fi.permissions, 
        fi.expires_at, fi.status,
        u.first_name as patient_first_name,
        u.last_name as patient_last_name
      FROM family_invitations fi
      JOIN users u ON fi.inviter_id = u.id
      WHERE fi.invitation_code = $1`,
      [invitation_code.toUpperCase()]
    );

    if (invitationResult.rowCount === 0) {
      return errorResponse('Invalid invitation code', 404);
    }

    const invitation = invitationResult.rows[0];

    // Check if expired
    if (new Date(invitation.expires_at) < new Date()) {
      return errorResponse('This invitation code has expired', 400);
    }

    // Check status
    if (invitation.status === 'approved') {
      return errorResponse('This invitation has already been used', 400);
    }

    if (invitation.status === 'rejected') {
      return errorResponse('This invitation was rejected', 400);
    }

    // Check if already requested
    const existingRequest = await query(
      `SELECT id, status FROM family_connection_requests 
       WHERE invitation_id = $1 AND family_member_id = $2`,
      [invitation.id, auth.userId]
    );

    if (existingRequest.rowCount && existingRequest.rowCount > 0) {
      const existing = existingRequest.rows[0];
      if (existing.status === 'pending') {
        return errorResponse('You have already requested to connect. Waiting for approval.', 400);
      }
      if (existing.status === 'rejected') {
        return errorResponse('Your connection request was rejected', 400);
      }
    }

    // Check if trying to connect to self
    if (invitation.inviter_id === auth.userId) {
      return errorResponse('You cannot connect to yourself', 400);
    }

    // Create connection request
    await query(
      `INSERT INTO family_connection_requests (
        invitation_id, patient_id, family_member_id, message, status
      ) VALUES ($1, $2, $3, $4, 'pending')
      ON CONFLICT (invitation_id, family_member_id) 
      DO UPDATE SET message = $4, status = 'pending', created_at = NOW()`,
      [invitation.id, invitation.inviter_id, auth.userId, message || null]
    );

    // Update invitation status to 'requested'
    await query(
      `UPDATE family_invitations 
       SET status = 'requested', requested_by = $1, requested_at = NOW()
       WHERE id = $2`,
      [auth.userId, invitation.id]
    );

    // TODO: Send push notification to patient

    return successResponse(
      {
        status: 'pending_approval',
        patient_name: `${invitation.patient_first_name} ${invitation.patient_last_name}`,
        relationship_type: invitation.relationship_type,
        message: 'Connection request sent. Waiting for patient approval.'
      },
      'Connection request sent successfully'
    );

  } catch (error) {
    console.error('Connect error:', error);
    return errorResponse('Failed to send connection request', 500);
  }
}

// GET - Get family member's connection status
async function getHandler(req: NextRequest, auth: JwtPayload) {
  try {
    // Get all connection requests by this family member
    const result = await query(
      `SELECT 
        fcr.id, fcr.status, fcr.message, fcr.created_at, fcr.responded_at,
        fi.relationship_type,
        u.id as patient_id,
        u.first_name as patient_first_name,
        u.last_name as patient_last_name
      FROM family_connection_requests fcr
      JOIN family_invitations fi ON fcr.invitation_id = fi.id
      JOIN users u ON fcr.patient_id = u.id
      WHERE fcr.family_member_id = $1
      ORDER BY fcr.created_at DESC`,
      [auth.userId]
    );

    // Get approved connections (from family_member_profiles)
    const connectionsResult = await query(
      `SELECT 
        fmp.user_id, fmp.relationship_type, fmp.linked_at,
        fmp.can_view_prescriptions, fmp.can_view_reminders,
        fmp.can_manage_reminders, fmp.can_receive_alerts,
        u.id as patient_id,
        u.first_name, u.last_name, u.email
      FROM family_member_profiles fmp
      JOIN users u ON fmp.linked_patient_id = u.id
      WHERE fmp.user_id = $1 AND fmp.linked_patient_id IS NOT NULL`,
      [auth.userId]
    );

    return successResponse({
      pending_requests: result.rows.filter(r => r.status === 'pending'),
      rejected_requests: result.rows.filter(r => r.status === 'rejected'),
      active_connections: connectionsResult.rows
    });

  } catch (error) {
    console.error('Get connections error:', error);
    return errorResponse('Failed to get connections', 500);
  }
}

export const POST = withFamilyAuth(handler);
export const GET = withFamilyAuth(getHandler);