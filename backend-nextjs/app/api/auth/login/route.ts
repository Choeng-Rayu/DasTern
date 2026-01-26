import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import bcrypt from 'bcryptjs';
import { signJwt } from '@/lib/jwt';
import { randomUUID } from 'crypto';
import { validateLogin } from '@/lib/validators/auth.validator';
import { successResponse, errorResponse, validationError } from '@/lib/utils/response';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // Validate input
    const validation = validateLogin(body);
    if (!validation.valid) {
      return validationError(validation.errors);
    }

    const { email, password, device_info } = body;

    // Find user
    const userResult = await query(
      `SELECT id, email, password_hash, first_name, last_name, role,
              phone_number, subscription_tier, onboarding_status, is_active
       FROM users 
       WHERE email = $1 OR phone_number = $1`,
      [email.toLowerCase()]
    );

    if (userResult.rowCount === 0) {
      return errorResponse('Invalid credentials', 401);
    }

    const user = userResult.rows[0];

    // Check if active
    if (!user.is_active) {
      return errorResponse('Account is deactivated', 403);
    }

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      // Log failed attempt
      await query(
        `INSERT INTO audit_logs (user_id, action, resource_type, ip_address, created_at)
         VALUES ($1, 'login_failed', 'auth', $2, NOW())`,
        [user.id, req.headers.get('x-forwarded-for') || 'unknown']
      );
      return errorResponse('Invalid credentials', 401);
    }

    // Generate tokens
    const accessToken = signJwt({
      userId: user.id,
      email: user.email,
      role: user.role,
      subscriptionTier: user.subscription_tier,
      onboardingStatus: user.onboarding_status
    });

    const refreshToken = randomUUID(); // Use built-in crypto
    const refreshExpires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

    // Store refresh token
    await query(
      `INSERT INTO user_sessions (user_id, refresh_token, device_info, ip_address, expires_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [user.id, refreshToken, device_info ? JSON.stringify(device_info) : null,
       req.headers.get('x-forwarded-for'), refreshExpires]
    );

    // Update last login
    await query('UPDATE users SET last_login_at = NOW() WHERE id = $1', [user.id]);

    // Log successful login
    await query(
      `INSERT INTO audit_logs (user_id, action, resource_type, ip_address, created_at)
       VALUES ($1, 'login_success', 'auth', $2, NOW())`,
      [user.id, req.headers.get('x-forwarded-for') || 'unknown']
    );

    // Determine next step
    const nextStep = getNextStep(user.onboarding_status, user.role);

    return successResponse(
      {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'Bearer',
        expires_in: 7 * 24 * 60 * 60,
        user: {
          id: user.id,
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          telephone: user.phone_number,
          role: user.role,
          subscription_tier: user.subscription_tier,
          onboarding_status: user.onboarding_status
        }
      },
      'Login successful',
      { next_step: nextStep }
    );

  } catch (error) {
    console.error('Login error:', error);
    return errorResponse('Login failed', 500);
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