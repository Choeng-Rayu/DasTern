import { NextRequest, NextResponse } from 'next/server';
import { verifyJwt } from '@/lib/jwt';
import { errorResponse } from '@/lib/utils/response';
import { JwtPayload, UserRole, OnboardingStatus } from '@/lib/types/auth.types';

export interface AuthOptions {
  roles?: UserRole[];
  requireActive?: boolean;      // Requires onboarding_status = 'active'
  allowPending?: boolean;       // Allows 'pending' status (for role selection)
  allowRoleSelected?: boolean;  // Allows 'role_selected' status (for profile completion)
}

export type AuthenticatedHandler = (
  req: NextRequest,
  auth: JwtPayload
) => Promise<NextResponse>;

/**
 * Main authentication middleware wrapper
 */
export function withAuth(
  handler: AuthenticatedHandler,
  options: AuthOptions = {}
) {
  return async (req: NextRequest): Promise<NextResponse> => {
    try {
      // Extract token from header
      const authHeader = req.headers.get('authorization');
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return errorResponse('Authorization token required', 401);
      }

      const token = authHeader.substring(7);
      const payload = verifyJwt(token) as JwtPayload | null;

      if (!payload) {
        return errorResponse('Invalid or expired token', 401);
      }

      // Check role permission
      if (options.roles && options.roles.length > 0) {
        if (!options.roles.includes(payload.role)) {
          return errorResponse(
            `Access denied. Required role: ${options.roles.join(' or ')}`,
            403
          );
        }
      }

      // Check onboarding status
      const status = payload.onboardingStatus;
      
      if (options.requireActive && status !== 'active') {
        return NextResponse.json(
          {
            success: false,
            error: 'Please complete your profile to access this resource',
            meta: {
              current_status: status,
              next_step: getNextStep(status, payload.role)
            }
          },
          { status: 403 }
        );
      }

      // For role selection endpoint - allow 'pending' status
      if (!options.allowPending && status === 'pending') {
        return NextResponse.json(
          {
            success: false,
            error: 'Please select your role first',
            meta: { next_step: 'select_role' }
          },
          { status: 403 }
        );
      }

      // For profile completion endpoint - allow 'role_selected' status
      if (!options.allowRoleSelected && status === 'role_selected') {
        return NextResponse.json(
          {
            success: false,
            error: 'Please complete your profile',
            meta: { next_step: 'complete_profile' }
          },
          { status: 403 }
        );
      }

      // Call the actual handler with auth payload
      return handler(req, payload);

    } catch (error) {
      console.error('Auth middleware error:', error);
      return errorResponse('Authentication failed', 401);
    }
  };
}

/**
 * Determine next step based on status and role
 */
function getNextStep(status: OnboardingStatus, role: UserRole): string {
  switch (status) {
    case 'pending':
      return 'select_role';
    case 'role_selected':
      return 'complete_profile';
    case 'profile_pending':
      return role === 'doctor' ? 'awaiting_verification' : 'complete_profile';
    case 'active':
      return 'dashboard';
    default:
      return 'unknown';
  }
}

// =============================================
// Pre-configured middleware for common use cases
// =============================================

/**
 * Requires fully onboarded user
 */
export const withActiveAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { requireActive: true });

/**
 * Allows user who just registered (for role selection)
 */
export const withPendingAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { allowPending: true });

/**
 * Allows user who selected role (for profile completion)
 */
export const withRoleSelectedAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { allowPending: true, allowRoleSelected: true });

/**
 * Patient-only access (must be active)
 */
export const withPatientAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { roles: ['patient', 'admin'], requireActive: true });

/**
 * Doctor-only access (must be active)
 */
export const withDoctorAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { roles: ['doctor', 'admin'], requireActive: true });

/**
 * Family member access (must be active)
 */
export const withFamilyAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { roles: ['family_member', 'admin'], requireActive: true });

/**
 * Admin-only access
 */
export const withAdminAuth = (handler: AuthenticatedHandler) =>
  withAuth(handler, { roles: ['admin'], requireActive: true });