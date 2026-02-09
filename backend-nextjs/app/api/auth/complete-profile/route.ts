import { NextRequest } from 'next/server';
import { query, getClient } from '@/lib/db';
import { signJwt } from '@/lib/jwt';
import { withRoleSelectedAuth } from '@/lib/middleware/auth';
import { validatePatientProfile } from '@/lib/validators/patient.validator';
import { validateDoctorProfile } from '@/lib/validators/doctor.validator';
import { validateFamilyProfile } from '@/lib/validators/family.validator';
import { successResponse, errorResponse, validationError } from '@/lib/utils/response';
import { JwtPayload } from '@/lib/types/auth.types';

// Define result type for profile completion
type ProfileResult = 
  | { success: true; user: any; profile: any; nextStep: string }
  | { success: false; error?: string; errors?: Record<string, string> };

async function handler(req: NextRequest, auth: JwtPayload) {
  try {
    const body = await req.json();

    // Get current user
    const userResult = await query(
      'SELECT id, role, onboarding_status FROM users WHERE id = $1',
      [auth.userId]
    );

    if (userResult.rowCount === 0) {
      return errorResponse('User not found', 404);
    }

    const user = userResult.rows[0];

    // Check status
    if (user.onboarding_status !== 'role_selected') {
      if (user.onboarding_status === 'pending') {
        return errorResponse('Please select a role first', 400);
      }
      if (user.onboarding_status === 'active') {
        return errorResponse('Profile already completed', 400);
      }
    }

    // Route to role-specific handler
    let result: ProfileResult;
    switch (user.role) {
      case 'patient':
        result = await completePatientProfile(auth.userId, body);
        break;
      case 'doctor':
        result = await completeDoctorProfile(auth.userId, body);
        break;
      case 'family_member':
        result = await completeFamilyProfile(auth.userId, body);
        break;
      default:
        return errorResponse('Invalid role', 400);
    }

    if (!result.success) {
      if (result.errors) {
        return validationError(result.errors);
      }
      return errorResponse(result.error || 'Profile completion failed', 400);
    }

    // Generate new token
    const newToken = signJwt({
      userId: result.user.id,
      email: result.user.email,
      role: result.user.role,
      subscriptionTier: result.user.subscription_tier,
      onboardingStatus: result.user.onboarding_status
    });

    return successResponse(
      {
        token: newToken,
        user: result.user,
        profile: result.profile
      },
      'Profile completed successfully',
      { next_step: result.nextStep }
    );

  } catch (error) {
    console.error('Profile completion error:', error);
    return errorResponse('Profile completion failed', 500);
  }
}

// =============================================
// PATIENT PROFILE COMPLETION
// =============================================
async function completePatientProfile(userId: string, data: any): Promise<ProfileResult> {
  // Validate
  const validation = validatePatientProfile(data);
  if (!validation.valid) {
    return { success: false, errors: validation.errors };
  }

  const client = await getClient();

  try {
    await client.query('BEGIN');

    // Create patient profile
    const profileResult = await client.query(
      `INSERT INTO patient_profiles (
        user_id, meal_schedule, use_custom_schedule,
        emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
        blood_type, medical_conditions, allergies
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      ON CONFLICT (user_id) DO UPDATE SET
        meal_schedule = EXCLUDED.meal_schedule,
        use_custom_schedule = EXCLUDED.use_custom_schedule,
        emergency_contact_name = EXCLUDED.emergency_contact_name,
        emergency_contact_phone = EXCLUDED.emergency_contact_phone,
        emergency_contact_relationship = EXCLUDED.emergency_contact_relationship,
        blood_type = EXCLUDED.blood_type,
        medical_conditions = EXCLUDED.medical_conditions,
        allergies = EXCLUDED.allergies,
        updated_at = NOW()
      RETURNING *`,
      [
        userId,
        JSON.stringify(data.meal_schedule),
        data.use_custom_schedule || false,
        data.emergency_contact_name,
        data.emergency_contact_phone,
        data.emergency_contact_relationship || null,
        data.blood_type || null,
        data.medical_conditions || [],
        data.allergies || []
      ]
    );

    // Update user status to active
    const userResult = await client.query(
      `UPDATE users SET
        onboarding_status = 'active',
        profile_completed_at = NOW(),
        updated_at = NOW()
      WHERE id = $1
      RETURNING id, email, first_name, last_name, role, onboarding_status, subscription_tier`,
      [userId]
    );

    await client.query('COMMIT');

    return {
      success: true,
      user: userResult.rows[0],
      profile: profileResult.rows[0],
      nextStep: 'dashboard'
    };

  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

// =============================================
// DOCTOR PROFILE COMPLETION
// =============================================
async function completeDoctorProfile(userId: string, data: any): Promise<ProfileResult> {
  // Validate
  const validation = validateDoctorProfile(data);
  if (!validation.valid) {
    return { success: false, errors: validation.errors };
  }

  const client = await getClient();

  try {
    await client.query('BEGIN');

    // Create doctor profile (pending verification)
    const profileResult = await client.query(
      `INSERT INTO doctor_profiles (
        user_id, license_number, specialization, hospital_name,
        years_of_experience, clinic_name, hospital_address,
        verification_status
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
      ON CONFLICT (user_id) DO UPDATE SET
        license_number = EXCLUDED.license_number,
        specialization = EXCLUDED.specialization,
        hospital_name = EXCLUDED.hospital_name,
        years_of_experience = EXCLUDED.years_of_experience,
        clinic_name = EXCLUDED.clinic_name,
        hospital_address = EXCLUDED.hospital_address,
        updated_at = NOW()
      RETURNING *`,
      [
        userId,
        data.license_number,
        data.specialization,
        data.hospital_name,
        data.years_of_experience,
        data.clinic_name || null,
        data.hospital_address || null
      ]
    );

    // Update user status to profile_pending (needs admin verification)
    const userResult = await client.query(
      `UPDATE users SET
        onboarding_status = 'profile_pending',
        profile_completed_at = NOW(),
        updated_at = NOW()
      WHERE id = $1
      RETURNING id, email, first_name, last_name, role, onboarding_status, subscription_tier`,
      [userId]
    );

    await client.query('COMMIT');

    return {
      success: true,
      user: userResult.rows[0],
      profile: profileResult.rows[0],
      nextStep: 'awaiting_verification'
    };

  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

// =============================================
// FAMILY MEMBER PROFILE COMPLETION (Updated)
// =============================================
async function completeFamilyProfile(userId: string, data: any): Promise<ProfileResult> {
  // Family member can complete profile WITHOUT invitation code
  // They will need to connect with patient later using /api/family/connect
  
  const client = await getClient();

  try {
    await client.query('BEGIN');

    // Create family member profile (without link - will be linked later)
    const profileResult = await client.query(
      `INSERT INTO family_member_profiles (
        user_id, relationship_type, linked_at
      ) VALUES ($1, $2, NULL)
      ON CONFLICT (user_id) DO UPDATE SET
        updated_at = NOW()
      RETURNING *`,
      [
        userId,
        data.preferred_relationship || null
      ]
    );

    // Update user status to active (they can use app, just not linked yet)
    const userResult = await client.query(
      `UPDATE users SET
        onboarding_status = 'active',
        profile_completed_at = NOW(),
        updated_at = NOW()
      WHERE id = $1
      RETURNING id, email, first_name, last_name, role, onboarding_status, subscription_tier`,
      [userId]
    );

    await client.query('COMMIT');

    return {
      success: true,
      user: userResult.rows[0],
      profile: {
        ...profileResult.rows[0],
        linked_patient_id: null,
        connection_status: 'not_connected'
      },
      nextStep: 'connect_to_patient'
    };

  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

export const POST = withRoleSelectedAuth(handler);