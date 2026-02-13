import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { withAuth } from '@/lib/middleware/auth';
import { successResponse, errorResponse } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

async function handler(req: NextRequest, auth: JwtPayload) {
  try {
    // Get base user info
    const userResult = await query(
      `SELECT id, email, first_name, last_name, phone_number, role,
              subscription_tier, onboarding_status, is_active, created_at, last_login_at
       FROM users WHERE id = $1`,
      [auth.userId]
    );

    if (userResult.rowCount === 0) {
      return errorResponse('User not found', 404);
    }

    const user = userResult.rows[0];

    // Get role-specific profile
    let profile = null;

    if (user.onboarding_status === 'active' || user.onboarding_status === 'profile_pending') {
      switch (user.role) {
        case 'patient':
          const patientResult = await query(
            `SELECT meal_schedule, emergency_contact_name, emergency_contact_phone,
                    blood_type, medical_conditions, allergies
             FROM patient_profiles WHERE user_id = $1`,
            [auth.userId]
          );
          profile = patientResult.rows[0] || null;
          break;

        case 'doctor':
          const doctorResult = await query(
            `SELECT license_number, specialization, hospital_name,
                    years_of_experience, verification_status
             FROM doctor_profiles WHERE user_id = $1`,
            [auth.userId]
          );
          profile = doctorResult.rows[0] || null;
          break;

        case 'family_member':
          const familyResult = await query(
            `SELECT fm.linked_patient_id, fm.relationship_type,
                    fm.can_view_prescriptions, fm.can_view_reminders,
                    u.first_name as patient_first_name, u.last_name as patient_last_name
             FROM family_member_profiles fm
             LEFT JOIN users u ON fm.linked_patient_id = u.id
             WHERE fm.user_id = $1`,
            [auth.userId]
          );
          profile = familyResult.rows[0] || null;
          break;
      }
    }

    // Determine next step
    const nextStep = getNextStep(user.onboarding_status, user.role);

    return successResponse({
      user: {
        id: user.id,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        telephone: user.phone_number,
        role: user.role,
        subscription_tier: user.subscription_tier,
        onboarding_status: user.onboarding_status,
        is_active: user.is_active,
        created_at: user.created_at,
        last_login_at: user.last_login_at
      },
      profile,
      next_step: nextStep
    });

  } catch (error) {
    console.error('Get user error:', error);
    return errorResponse('Failed to get user info', 500);
  }
}

function getNextStep(status: string, role: string): string {
  switch (status) {
    case 'pending': return 'select_role';
    case 'role_selected': return 'complete_profile';
    case 'profile_pending': return role === 'doctor' ? 'awaiting_verification' : 'dashboard';
    case 'active': return 'dashboard';
    default: return 'unknown';
  }
}

export const GET = withAuth(handler, { allowPending: true, allowRoleSelected: true });