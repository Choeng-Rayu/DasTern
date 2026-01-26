import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { signJwt } from '@/lib/jwt';
import { v4 as uuidv4 } from 'uuid';
import { successResponse, errorResponse } from '@/lib/utils/response';

export async function POST(req: NextRequest) {
  try {
    const { refresh_token } = await req.json();

    if (!refresh_token) {
      return errorResponse('Refresh token is required', 400);
    }

    // Find session
    const sessionResult = await query(
      `SELECT s.id, s.user_id, s.expires_at,
              u.email, u.role, u.subscription_tier, u.onboarding_status, u.is_active
       FROM user_sessions s
       JOIN users u ON s.user_id = u.id
       WHERE s.refresh_token = $1 AND s.is_active = true`,
      [refresh_token]
    );

    if (sessionResult.rowCount === 0) {
      return errorResponse('Invalid refresh token', 401);
    }

    const session = sessionResult.rows[0];

    // Check expiry
    if (new Date(session.expires_at) < new Date()) {
      await query('DELETE FROM user_sessions WHERE id = $1', [session.id]);
      return errorResponse('Refresh token expired', 401);
    }

    // Check user active
    if (!session.is_active) {
      await query('DELETE FROM user_sessions WHERE user_id = $1', [session.user_id]);
      return errorResponse('Account deactivated', 403);
    }

    // Generate new tokens
    const newAccessToken = signJwt({
      userId: session.user_id,
      email: session.email,
      role: session.role,
      subscriptionTier: session.subscription_tier,
      onboardingStatus: session.onboarding_status
    });

    const newRefreshToken = uuidv4();
    const newExpires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);

    // Rotate refresh token
    await query('DELETE FROM user_sessions WHERE id = $1', [session.id]);
    await query(
      `INSERT INTO user_sessions (user_id, refresh_token, expires_at, created_at)
       VALUES ($1, $2, $3, NOW())`,
      [session.user_id, newRefreshToken, newExpires]
    );

    return successResponse({
      access_token: newAccessToken,
      refresh_token: newRefreshToken,
      token_type: 'Bearer',
      expires_in: 7 * 24 * 60 * 60
    });

  } catch (error) {
    console.error('Token refresh error:', error);
    return errorResponse('Token refresh failed', 500);
  }
}