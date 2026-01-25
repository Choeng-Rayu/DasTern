/**
 * DasTern Healthcare System - TypeScript Types
 * Matching database schema for prescription OCR, medications, reminders, and reports
 */

// =============================================
// ENUMS AND BASIC TYPES
// =============================================

export type UserRole = 'patient' | 'doctor' | 'admin';
export type SubscriptionTier = 'free' | 'premium';
export type PrescriptionStatus = 'pending' | 'processing' | 'ocr_completed' | 'ai_processed' | 'completed' | 'error' | 'archived';
export type RelationshipStatus = 'pending' | 'active' | 'inactive' | 'blocked';
export type NotificationType = 'reminder' | 'alert' | 'message' | 'system';
export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';
export type ReminderLogStatus = 'taken' | 'missed' | 'snoozed' | 'skipped' | 'pending';
export type MedicationForm = 'tablet' | 'capsule' | 'syrup' | 'injection' | 'cream' | 'drops' | 'inhaler' | 'patch' | 'other';
export type ReportType = 'medical_summary' | 'risk_analysis' | 'trend_analysis' | 'prescription_history' | 'medication_adherence';
export type TimeSlot = 'morning' | 'noon' | 'afternoon' | 'evening' | 'night';

// =============================================
// USER MANAGEMENT TYPES
// =============================================

export interface User {
  id: string;
  email: string;
  password_hash?: string; // Excluded in responses
  role: UserRole;
  subscription_tier: SubscriptionTier;
  subscription_expires_at?: Date;

  // Profile information
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  date_of_birth?: Date;
  gender?: string;
  profile_picture_url?: string;

  // Preferences
  language_preference: string;
  timezone: string;
  notification_preferences: NotificationPreferences;

  // Medical information (for patients)
  medical_conditions?: string[];
  allergies?: string[];
  blood_type?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;

  // Professional information (for doctors)
  license_number?: string;
  specialization?: string;
  hospital_affiliation?: string;
  years_of_experience?: number;
  is_verified?: boolean;

  // System fields
  email_verified: boolean;
  is_active: boolean;
  last_login_at?: Date;
  created_at: Date;
  updated_at: Date;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  sms: boolean;
  reminder_advance_minutes?: number;
}

export interface UserSession {
  id: string;
  user_id: string;
  refresh_token: string;
  device_info?: DeviceInfo;
  ip_address?: string;
  expires_at: Date;
  created_at: Date;
}

export interface DeviceInfo {
  device_type: string;
  device_name?: string;
  os?: string;
  app_version?: string;
}

// =============================================
// PRESCRIPTION TYPES
// =============================================

export interface Prescription {
  id: string;
  patient_id: string;
  doctor_id?: string;

  // Image and OCR data
  original_image_url: string;
  thumbnail_url?: string;
  image_metadata?: ImageMetadata;

  // OCR processing results
  ocr_raw_text?: string;
  ocr_corrected_text?: string;
  ocr_structured_data?: OCRStructuredData;
  ocr_confidence_score?: number;
  ocr_language_detected?: string;
  ocr_processing_time?: number;

  // AI processing results (premium feature)
  ai_report?: AIReport;
  ai_confidence_score?: number;
  ai_processing_time?: number;
  ai_warnings?: string[];

  // Prescription metadata extracted from document
  hospital_name?: string;
  hospital_address?: string;
  prescription_number?: string;
  patient_name_on_doc?: string;
  patient_age?: number;
  patient_gender?: string;
  diagnosis?: string;
  department?: string;
  prescribing_doctor_name?: string;
  prescription_date?: Date;

  // Status and workflow
  status: PrescriptionStatus;
  processing_started_at?: Date;
  processing_completed_at?: Date;
  error_message?: string;

  // System fields
  created_at: Date;
  updated_at: Date;

  // Relations (populated when needed)
  medications?: Medication[];
  reminders?: MedicationReminder[];
}

export interface ImageMetadata {
  size: number;
  format: string;
  width: number;
  height: number;
  original_filename?: string;
}

export interface OCRStructuredData {
  header?: PrescriptionHeader;
  medications: ExtractedMedication[];
  footer?: PrescriptionFooter;
  raw_fields?: Record<string, string>;
}

export interface PrescriptionHeader {
  hospital_name?: string;
  hospital_logo_detected?: boolean;
  patient_id?: string;
  patient_name?: string;
  age?: number;
  gender?: string;
  diagnosis?: string;
  department?: string;
  date?: string;
}

export interface PrescriptionFooter {
  doctor_name?: string;
  doctor_signature_detected?: boolean;
  date?: string;
  notes?: string;
}

export interface ExtractedMedication {
  sequence_number: number;
  name: string;
  quantity?: number;
  unit?: string;
  dosage_schedule: DosageSchedule;
  special_instructions?: string;
  confidence_score?: number;
}

// =============================================
// MEDICATION TYPES
// =============================================

export interface Medication {
  id: string;
  prescription_id: string;
  sequence_number: number;

  // Medication details
  name: string;
  generic_name?: string;
  brand_name?: string;
  strength?: string;
  form: MedicationForm;

  // Quantity and duration
  quantity: number;
  quantity_unit: string;
  duration_days?: number;

  // Dosage schedule (structured from Cambodian prescription format)
  dosage_schedule: DosageSchedule;

  // Additional instructions
  instructions?: string;
  take_with_food?: boolean;
  take_before_meal?: boolean;
  take_after_meal?: boolean;

  // AI analysis (premium feature)
  ai_drug_interactions?: string[];
  ai_side_effects?: string[];
  ai_warnings?: string[];
  ai_contraindications?: string[];
  ai_description?: string;

  // System fields
  is_active: boolean;
  created_at: Date;
  updated_at: Date;

  // Relations
  reminders?: MedicationReminder[];
}

/**
 * Dosage Schedule matching Cambodian prescription format
 * Time slots: morning (6-8), noon (11-12), afternoon (05-06), night (08-10)
 */
export interface DosageSchedule {
  morning?: DosageAmount;   // ព្រឹក (6-8 AM)
  noon?: DosageAmount;      // ថ្ងៃត្រង់ (11-12 PM)
  afternoon?: DosageAmount; // ល្ងាច (05-06 PM)
  evening?: DosageAmount;   // យប់ (08-10 PM) - same as night in some formats
  night?: DosageAmount;     // Alternative naming

  // Custom time slots for flexibility
  custom_times?: CustomDosageTime[];

  // Frequency metadata
  times_per_day?: number;
  total_daily_dose?: string;
}

export interface DosageAmount {
  dose: number;
  unit?: string;
  time_range_start?: string; // e.g., "06:00"
  time_range_end?: string;   // e.g., "08:00"
  preferred_time?: string;   // e.g., "07:00"
}

export interface CustomDosageTime {
  time: string;
  dose: number;
  unit?: string;
  label?: string;
}

// =============================================
// MEDICATION REMINDER TYPES
// =============================================

export interface MedicationReminder {
  id: string;
  medication_id: string;
  prescription_id: string;
  patient_id: string;

  // Reminder configuration
  time_slot: TimeSlot;
  scheduled_time: string; // HH:MM format
  dose_amount: number;
  dose_unit?: string;

  // Schedule
  start_date: Date;
  end_date?: Date;
  days_of_week: number[]; // 1-7, where 1=Monday

  // Reminder settings
  is_active: boolean;
  snooze_duration_minutes: number;
  advance_notification_minutes: number;
  notification_sound?: string;

  // Tracking
  total_doses: number;
  completed_doses: number;
  missed_doses: number;
  adherence_rate?: number;

  // Last activity
  last_taken_at?: Date;
  last_missed_at?: Date;
  next_reminder_at?: Date;

  // System fields
  created_at: Date;
  updated_at: Date;

  // Relations
  medication?: Medication;
  logs?: MedicationReminderLog[];
}

export interface MedicationReminderLog {
  id: string;
  reminder_id: string;
  medication_id: string;
  patient_id: string;

  // Log details
  scheduled_date: Date;
  scheduled_time: string;
  actual_time?: Date;
  status: ReminderLogStatus;

  // Additional info
  notes?: string;
  dose_taken?: number;
  skipped_reason?: string;
  snoozed_until?: Date;

  // Device info
  logged_from_device?: string;

  created_at: Date;
}

// =============================================
// AI REPORT TYPES
// =============================================

export interface AIReport {
  id: string;
  prescription_id: string;
  user_id: string;
  report_type: ReportType;

  // Report content
  summary: string;
  detailed_analysis: DetailedAnalysis;
  recommendations?: string[];
  warnings?: AIWarning[];

  // AI metadata
  ai_model_version: string;
  ai_confidence_score: number;
  generation_time: number;
  language: string;

  // Export info
  exported_at?: Date;
  export_format?: string;
  export_url?: string;

  // Sharing
  shared_with_doctor: boolean;
  shared_with_family: boolean;

  // System fields
  created_at: Date;
  updated_at: Date;
}

export interface DetailedAnalysis {
  medications_analysis: MedicationAnalysis[];
  drug_interactions?: DrugInteraction[];
  overall_risk_level?: 'low' | 'medium' | 'high';
  adherence_prediction?: number;
  treatment_duration?: TreatmentDuration;
}

export interface MedicationAnalysis {
  medication_id: string;
  medication_name: string;
  purpose?: string;
  mechanism?: string;
  common_side_effects?: string[];
  important_warnings?: string[];
  food_interactions?: string[];
}

export interface DrugInteraction {
  medication_1: string;
  medication_2: string;
  interaction_type: 'major' | 'moderate' | 'minor';
  description: string;
  recommendation: string;
}

export interface TreatmentDuration {
  estimated_days: number;
  end_date: Date;
  follow_up_recommended: boolean;
  follow_up_date?: Date;
}

export interface AIWarning {
  type: 'allergy' | 'interaction' | 'contraindication' | 'dosage' | 'general';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  medication_id?: string;
  action_required?: string;
}

// =============================================
// FAMILY/CAREGIVER TYPES
// =============================================

export interface FamilyRelationship {
  id: string;
  patient_id: string;
  family_member_id: string;

  // Relationship details
  relationship_type: string; // 'parent', 'child', 'spouse', 'sibling', 'caregiver', 'other'
  status: RelationshipStatus;

  // Permissions
  can_view_prescriptions: boolean;
  can_view_reminders: boolean;
  can_view_reports: boolean;
  can_receive_alerts: boolean;
  can_log_medications: boolean;

  // Invitation
  invitation_code?: string;
  invitation_expires_at?: Date;

  // System fields
  established_at?: Date;
  created_at: Date;
  updated_at: Date;
}

// =============================================
// NOTIFICATION TYPES
// =============================================

export interface Notification {
  id: string;
  user_id: string;

  // Notification content
  type: NotificationType;
  title: string;
  message: string;

  // Metadata
  data?: NotificationData;
  action_url?: string;

  // Delivery status
  is_read: boolean;
  read_at?: Date;
  sent_at?: Date;

  // System fields
  created_at: Date;
  expires_at?: Date;
}

export interface NotificationData {
  reminder_id?: string;
  medication_id?: string;
  prescription_id?: string;
  patient_id?: string;
  [key: string]: any;
}

// =============================================
// API REQUEST/RESPONSE TYPES
// =============================================

// OCR Upload Request
export interface PrescriptionUploadRequest {
  image: File | string; // File or base64
  patient_id: string;
  doctor_id?: string;
  language_hint?: string;
}

// OCR Response
export interface OCRResponse {
  prescription_id: string;
  status: PrescriptionStatus;
  ocr_text: string;
  ocr_confidence: number;
  structured_data: OCRStructuredData;
  processing_time: number;
}

// Medication extraction response
export interface MedicationExtractionResponse {
  prescription_id: string;
  medications: Medication[];
  extraction_confidence: number;
  warnings?: string[];
}

// Reminder creation request
export interface CreateRemindersRequest {
  prescription_id: string;
  medication_id?: string;
  patient_id: string;
  use_default_times?: boolean;
  custom_times?: {
    morning?: string;
    noon?: string;
    afternoon?: string;
    evening?: string;
    night?: string;
  };
  start_date?: string;
  advance_notification_minutes?: number;
}

// Reminder response
export interface ReminderResponse {
  reminder_id: string;
  medication_id: string;
  medication_name: string;
  time_slot: TimeSlot;
  scheduled_time: string;
  dose_amount: number;
  dose_unit?: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
}

// Bulk reminders response
export interface BulkRemindersResponse {
  prescription_id: string;
  reminders_created: number;
  reminders: ReminderResponse[];
  failed?: { medication_id: string; error: string }[];
}

// Report request
export interface GenerateReportRequest {
  prescription_id: string;
  report_type: ReportType;
  include_ai_analysis?: boolean;
  language?: string;
}

// Report response
export interface ReportResponse {
  report_id: string;
  report_type: ReportType;
  prescription_id: string;
  summary: string;
  detailed_analysis: DetailedAnalysis;
  recommendations: string[];
  warnings: AIWarning[];
  generated_at: Date;
  export_available: boolean;
}

// Log medication taken
export interface LogMedicationRequest {
  reminder_id: string;
  status: ReminderLogStatus;
  actual_time?: string;
  notes?: string;
  dose_taken?: number;
  skipped_reason?: string;
}

// Today's reminders response
export interface TodayRemindersResponse {
  date: string;
  reminders: TodayReminderItem[];
  adherence_today: number;
  total_today: number;
  completed_today: number;
}

export interface TodayReminderItem {
  reminder_id: string;
  medication_id: string;
  prescription_id: string;
  medication_name: string;
  medication_strength?: string;
  time_slot: TimeSlot;
  scheduled_time: string;
  dose_amount: number;
  dose_unit?: string;
  status: ReminderLogStatus;
  taken_at?: Date;
  is_overdue: boolean;
}

// History response
export interface PrescriptionHistoryResponse {
  prescriptions: PrescriptionSummary[];
  total_count: number;
  page: number;
  per_page: number;
  has_more: boolean;
}

export interface PrescriptionSummary {
  id: string;
  prescription_date?: Date;
  hospital_name?: string;
  diagnosis?: string;
  medication_count: number;
  status: PrescriptionStatus;
  thumbnail_url?: string;
  created_at: Date;
}

// =============================================
// DEFAULT TIME SLOTS CONFIGURATION
// =============================================

export const DEFAULT_TIME_SLOTS: Record<TimeSlot, { start: string; end: string; default: string }> = {
  morning: { start: '06:00', end: '08:00', default: '07:00' },
  noon: { start: '11:00', end: '12:00', default: '11:30' },
  afternoon: { start: '17:00', end: '18:00', default: '17:30' },
  evening: { start: '20:00', end: '22:00', default: '20:00' },
  night: { start: '20:00', end: '22:00', default: '21:00' },
};

// Khmer time slot mapping (from prescription image)
export const KHMER_TIME_SLOT_MAP: Record<string, TimeSlot> = {
  'ព្រឹក': 'morning',       // Morning (6-8)
  'ថ្ងៃត្រង់': 'noon',       // Noon (11-12)
  'ល្ងាច': 'afternoon',     // Afternoon/Evening (05-06)
  'យប់': 'night',          // Night (08-10)
};
