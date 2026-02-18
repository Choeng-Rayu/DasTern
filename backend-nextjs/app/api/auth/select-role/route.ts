import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { signJwt } from '@/lib/jwt';
import { withPendingAuth } from '@/lib/middleware/auth';
import { validateRoleSelection } from '@/lib/validators/auth.validator';
import { successResponse, errorResponse, validationError } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

async function handler(req: NextRequest, auth: JwtPayload) {
  try {
    const body = await req.json();

    // Validate input
    const validation = validateRoleSelection(body);
    if (!validation.valid) {
      return validationError(validation.errors);
    }

    const { role } = body;

    // Check current status
    const userResult = await query(
      'SELECT id, onboarding_status FROM users WHERE id = $1',
      [auth.userId] 
    );

    if (userResult.rowCount === 0) {
      return errorResponse('User not found', 404);
    }

    const user = userResult.rows[0];

    // Verify user can still select role
    // if (user.onboarding_status !== 'unassigned') {
    //   return errorResponse('Role already selected and cannot be changed', 400);
    // }

    // Update role
    const updateResult = await query(
      `UPDATE users SET 
        role = $1,
        onboarding_status = 'role_selected',
        role_selected_at = NOW(),
        updated_at = NOW()
      WHERE id = $2
      RETURNING id, email, first_name, last_name, role, onboarding_status, subscription_tier`,
      [role, auth.userId]
    );

    const updatedUser = updateResult.rows[0];

    // Generate new token with updated role
    const newToken = signJwt({
      userId: updatedUser.id,
      email: updatedUser.email,
      role: updatedUser.role,
      subscriptionTier: updatedUser.subscription_tier,
      onboardingStatus: updatedUser.onboarding_status
    });

    // Get required fields for the role
    const requiredFields = getRequiredFieldsForRole(role);

    return successResponse(
      {
        token: newToken,
        user: {
          id: updatedUser.id,
          email: updatedUser.email,
          first_name: updatedUser.first_name,
          last_name: updatedUser.last_name,
          role: updatedUser.role,
          onboarding_status: updatedUser.onboarding_status
        }
      },
      'Role selected successfully',
      { 
        next_step: 'complete_profile',
        required_fields: requiredFields
      }
    );

  } catch (error) {
    console.error('Role selection error:', error);
    return errorResponse('Role selection failed', 500);
  }
}

function getRequiredFieldsForRole(role: string): string[] {
  switch (role) {
    case 'patient':
      return [
        'meal_schedule',
        'emergency_contact_name',
        'emergency_contact_phone'
      ];
    case 'doctor':
      return [
        'license_number',
        'specialization',
        'hospital_name',
        'years_of_experience'
      ];
    case 'family_member':
      return ['invitation_code'];
    default:
      return [];
  }
}

export const POST = withPendingAuth(handler);