import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import bcrypt from 'bcryptjs';
import { signJwt } from '@/lib/jwt';
import { validateRegister } from '@/lib/validators/auth.validator';
import { successResponse, errorResponse, validationError } from '@/lib/utils/response';
import { toPostgresDate } from '@/lib/utils/date.utils';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // Validate input
    const validation = validateRegister(body);
    if (!validation.valid) {
      return validationError(validation.errors);
    }

    const { email, telephone, password, first_name, last_name, gender, date_of_birth } = body;

    const formattedDob = toPostgresDate(date_of_birth);

    // Check if user exists
    const exists = await query(
      'SELECT id, email, phone_number FROM users WHERE email = $1 OR phone_number = $2',
      [email.toLowerCase(), telephone]
    );

    if (exists.rowCount && exists.rowCount > 0) {
      const existing = exists.rows[0];
      if (existing.email === email.toLowerCase()) {
        return errorResponse('Email already registered', 409);
      }
      return errorResponse('Phone number already registered', 409);
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 12);

    // Create user (no role yet - will be selected in next step)
    const result = await query(
      `INSERT INTO users (
        id, email, first_name, last_name, phone_number, gender, date_of_birth, password_hash, 
        role, onboarding_status, created_at, updated_at
      ) VALUES (
        uuid_generate_v4(), $1, $2, $3, $4, $5, $6, $7,
        'patient', 'registered', NOW(), NOW()
      )
      RETURNING id, email, first_name, last_name, phone_number, gender, date_of_birth, role, onboarding_status, created_at`,
      [email.toLowerCase(), first_name, last_name, telephone, gender, formattedDob, passwordHash]
    );

    const user = result.rows[0];

    // Generate token
    const token = signJwt({
      userId: user.id,
      email: user.email,
      role: user.role,
      subscriptionTier: 'free',
      onboardingStatus: user.onboarding_status
    });

    // Log registration
    await query(
      `INSERT INTO audit_logs (user_id, action, resource_type, ip_address, created_at)
       VALUES ($1, 'register', 'auth', $2, NOW())`,
      [user.id, req.headers.get('x-forwarded-for') || 'unknown']
    );

    return successResponse(
      {
        token,
        user: {
          id: user.id,
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          telephone: user.phone_number,
          gender: user.gender,
          birth_of_date: user.date_of_birth,
          role: user.role,
          onboarding_status: user.onboarding_status
        }
      },
      'Registration successful',
      { next_step: 'select_role' },
      201
    );

  } catch (error) {
    console.error('Registration error:', error);
    return errorResponse('Registration failed', 500);
  }
}