/**
 * TypeScript types matching database schema
 */

export type UserRole = 'patient' | 'doctor' | 'admin';
export type SubscriptionTier = 'free' | 'premium';
export type PrescriptionStatus = 'processing' | 'completed' | 'error' | 'archived';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  subscription_tier: SubscriptionTier;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  created_at: Date;
  updated_at: Date;
}

export interface Prescription {
  id: string;
  patient_id: string;
  doctor_id?: string;
  original_image_url: string;
  thumbnail_url?: string;
  ocr_raw_text?: string;
  ocr_corrected_text?: string;
  ocr_confidence_score?: number;
  ai_report?: any;
  ai_confidence_score?: number;
  status: PrescriptionStatus;
  prescription_date?: Date;
  created_at: Date;
  updated_at: Date;
}

export interface Medication {
  id: string;
  prescription_id: string;
  name: string;
  generic_name?: string;
  brand_name?: string;
  strength?: string;
  form?: string;
  dosage?: string;
  frequency?: string;
  duration?: string;
  instructions?: string;
  take_with_food?: boolean;
  ai_drug_interactions?: string[];
  ai_side_effects?: string[];
  ai_warnings?: string[];
  created_at: Date;
  updated_at: Date;
}

export interface MedicationReminder {
  id: string;
  medication_id: string;
  patient_id: string;
  reminder_times: string[];
  days_of_week: number[];
  start_date: Date;
  end_date?: Date;
  is_active: boolean;
  created_at: Date;
  updated_at: Date;
}

// API Response types
export interface OCRResponse {
  prescription_id: string;
  ocr_text: string;
  ocr_confidence: number;
  medications: Medication[];
  status: string;
}

export interface ReminderResponse {
  reminder_id: string;
  medication_name: string;
  times: string[];
  start_date: string;
  end_date?: string;
}
