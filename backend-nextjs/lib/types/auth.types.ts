export type UserRole = 'patient' | 'doctor' | 'family_member' | 'admin';
export type OnboardingStatus = 'pending' | 'role_selected' | 'profile_pending' | 'active';
export type SubscriptionTier = 'free' | 'premium';

export interface JwtPayload {
  userId: string;
  email: string;
  role: UserRole;
  subscriptionTier: SubscriptionTier;
  onboardingStatus: OnboardingStatus;
  iat?: number;
  exp?: number;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  role: UserRole;
  subscription_tier: SubscriptionTier;
  onboarding_status: OnboardingStatus;
  is_active: boolean;
  created_at: Date;
}

export interface PatientProfile {
  id: string;
  user_id: string;
  meal_schedule: MealSchedule;
  use_custom_schedule: boolean;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  emergency_contact_relationship: string | null;
  blood_type: string | null;
  medical_conditions: string[];
  allergies: string[];
}

export interface MealSchedule {
  morning: string;
  noon: string;
  evening: string;
  night: string;
  custom?: { [key: string]: string };
}

export interface DoctorProfile {
  id: string;
  user_id: string;
  license_number: string;
  specialization: string;
  hospital_name: string;
  years_of_experience: number;
  verification_status: 'pending' | 'verified' | 'rejected';
}

export interface FamilyMemberProfile {
  id: string;
  user_id: string;
  linked_patient_id: string | null;
  relationship_type: string | null;
  can_view_prescriptions: boolean;
  can_view_reminders: boolean;
  can_manage_reminders: boolean;
  can_receive_alerts: boolean;
}