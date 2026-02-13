import { NextRequest } from 'next/server';
import { query, getClient } from '@/lib/db';
import { withPatientAuth } from '@/lib/middleware/auth';
import { successResponse, errorResponse } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

interface RouteParams {
  params: Promise<{ requestId: string }>;
}

// PATCH - Approve or reject connection request
async function handler(req: NextRequest, auth: JwtPayload, { params }: RouteParams) {
  const { requestId } = await params;
  
  try {
    const body = await req.json();
    const { action, rejection_reason } = body; // action: 'approve' | 'reject'

    if (!action || !['approve', 'reject'].includes(action)) {
      return errorResponse('Action must be "approve" or "reject"', 400);
    }

    // Get the request
    const requestResult = await query(
      `SELECT 
        fcr.id, fcr.invitation_id, fcr.family_member_id, fcr.status,
        fi.inviter_id, fi.relationship_type, fi.permissions
      FROM family_connection_requests fcr
      JOIN family_invitations fi ON fcr.invitation_id = fi.id
      WHERE fcr.id = $1`,
      [requestId]
    );

    if (requestResult.rowCount === 0) {
      return errorResponse('Connection request not found', 404);
    }

    const request = requestResult.rows[0];

    // Verify ownership
    if (request.inviter_id !== auth.userId) {
      return errorResponse('You can only respond to your own connection requests', 403);
    }

    // Check if already responded
    if (request.status !== 'pending') {
      return errorResponse(`This request has already been ${request.status}`, 400);
    }

    const client = await getClient();

    try {
      await client.query('BEGIN');

      if (action === 'approve') {
        // Update request status
        await client.query(
          `UPDATE family_connection_requests 
           SET status = 'approved', responded_at = NOW()
           WHERE id = $1`,
          [requestId]
        );

        // Update invitation status
        await client.query(
          `UPDATE family_invitations 
           SET status = 'approved', approved_at = NOW()
           WHERE id = $1`,
          [request.invitation_id]
        );

        const permissions = request.permissions || {};

        // Create or update family member profile with link
        await client.query(
          `INSERT INTO family_member_profiles (
            user_id, linked_patient_id, relationship_type,
            can_view_prescriptions, can_view_reminders,
            can_manage_reminders, can_receive_alerts, linked_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
          ON CONFLICT (user_id) DO UPDATE SET
            linked_patient_id = $2,
            relationship_type = $3,
            can_view_prescriptions = $4,
            can_view_reminders = $5,
            can_manage_reminders = $6,
            can_receive_alerts = $7,
            linked_at = NOW(),
            updated_at = NOW()`,
          [
            request.family_member_id,
            auth.userId,
            request.relationship_type,
            permissions.can_view_prescriptions || false,
            permissions.can_view_reminders || true,
            permissions.can_manage_reminders || false,
            permissions.can_receive_alerts || true
          ]
        );

        // Update family member's onboarding status to active
        await client.query(
          `UPDATE users 
           SET onboarding_status = 'active', profile_completed_at = NOW()
           WHERE id = $1 AND onboarding_status != 'active'`,
          [request.family_member_id]
        );

        await client.query('COMMIT');

        // TODO: Send push notification to family member

        // Get family member info for response
        const familyMemberResult = await query(
          `SELECT first_name, last_name, email FROM users WHERE id = $1`,
          [request.family_member_id]
        );

        return successResponse(
          {
            status: 'approved',
            family_member: familyMemberResult.rows[0],
            relationship_type: request.relationship_type
          },
          'Connection approved successfully'
        );

      } else {
        // Reject
        await client.query(
          `UPDATE family_connection_requests 
           SET status = 'rejected', responded_at = NOW()
           WHERE id = $1`,
          [requestId]
        );

        await client.query(
          `UPDATE family_invitations 
           SET status = 'rejected', rejected_at = NOW(), rejection_reason = $1
           WHERE id = $2`,
          [rejection_reason || null, request.invitation_id]
        );

        await client.query('COMMIT');

        // TODO: Send push notification to family member

        return successResponse(
          { status: 'rejected' },
          'Connection request rejected'
        );
      }

    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }

  } catch (error) {
    console.error('Respond to request error:', error);
    return errorResponse('Failed to respond to connection request', 500);
  }
}

// Wrapper to pass params
export const PATCH = (req: NextRequest, context: RouteParams) => 
  withPatientAuth((req, auth) => handler(req, auth, context))(req);