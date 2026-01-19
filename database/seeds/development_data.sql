-- Development Seed Data for DasTern V2
-- This file contains sample data for development and testing

BEGIN;

-- Insert subscription plans
INSERT INTO subscription_plans (id, name, tier, price_monthly, price_yearly, features, limits, is_active) VALUES
(uuid_generate_v4(), 'Free Plan', 'free', 0.00, 0.00, 
 '["prescription_scan", "ocr_extraction", "manual_edit", "medication_reminders", "basic_history", "doctor_patient_sharing"]',
 '{"max_prescriptions": 10, "ai_requests": 0, "export_formats": ["text"], "chat_messages": 0}',
 true),
(uuid_generate_v4(), 'Premium Plan', 'premium', 0.50, 5.00,
 '["prescription_scan", "ocr_extraction", "manual_edit", "medication_reminders", "unlimited_history", "ai_reports", "ai_chat", "ocr_correction", "pdf_export", "risk_alerts", "trend_analysis", "priority_support"]',
 '{"max_prescriptions": -1, "ai_requests": 1000, "export_formats": ["text", "pdf", "json"], "chat_messages": 500}',
 true);

-- Insert sample users
-- Admin user
INSERT INTO users (id, email, password_hash, role, first_name, last_name, is_active, email_verified, created_at) VALUES
(uuid_generate_v4(), 'admin@dastern.com', crypt('admin123', gen_salt('bf')), 'admin', 'System', 'Administrator', true, true, NOW());

-- Sample doctors
INSERT INTO users (id, email, password_hash, role, first_name, last_name, phone_number, specialization, license_number, hospital_affiliation, years_of_experience, is_active, email_verified, language_preference, created_at) VALUES
(uuid_generate_v4(), 'dr.smith@hospital.com', crypt('doctor123', gen_salt('bf')), 'doctor', 'John', 'Smith', '+1234567890', 'Internal Medicine', 'MD12345', 'General Hospital', 15, true, true, 'en', NOW()),
(uuid_generate_v4(), 'dr.johnson@clinic.com', crypt('doctor123', gen_salt('bf')), 'doctor', 'Sarah', 'Johnson', '+1234567891', 'Pediatrics', 'MD12346', 'Children Clinic', 8, true, true, 'en', NOW()),
(uuid_generate_v4(), 'dr.chen@medical.com', crypt('doctor123', gen_salt('bf')), 'doctor', 'Wei', 'Chen', '+1234567892', 'Cardiology', 'MD12347', 'Heart Center', 12, true, true, 'en', NOW());

-- Sample patients (free tier)
INSERT INTO users (id, email, password_hash, role, first_name, last_name, phone_number, date_of_birth, gender, medical_conditions, allergies, emergency_contact_name, emergency_contact_phone, is_active, email_verified, language_preference, created_at) VALUES
(uuid_generate_v4(), 'patient1@email.com', crypt('patient123', gen_salt('bf')), 'patient', 'Alice', 'Wilson', '+1234567893', '1985-03-15', 'female', '{"hypertension", "diabetes"}', '{"penicillin", "shellfish"}', 'Bob Wilson', '+1234567894', true, true, 'en', NOW()),
(uuid_generate_v4(), 'patient2@email.com', crypt('patient123', gen_salt('bf')), 'patient', 'Michael', 'Brown', '+1234567895', '1978-07-22', 'male', '{"asthma"}', '{"pollen"}', 'Lisa Brown', '+1234567896', true, true, 'en', NOW()),
(uuid_generate_v4(), 'patient3@email.com', crypt('patient123', gen_salt('bf')), 'patient', 'Emma', 'Davis', '+1234567897', '1992-11-08', 'female', '{}', '{}', 'James Davis', '+1234567898', true, true, 'fr', NOW());

-- Sample patients (premium tier)
INSERT INTO users (id, email, password_hash, role, subscription_tier, subscription_expires_at, first_name, last_name, phone_number, date_of_birth, gender, medical_conditions, allergies, emergency_contact_name, emergency_contact_phone, is_active, email_verified, language_preference, created_at) VALUES
(uuid_generate_v4(), 'premium1@email.com', crypt('patient123', gen_salt('bf')), 'patient', 'premium', NOW() + INTERVAL '1 month', 'Robert', 'Taylor', '+1234567899', '1980-05-12', 'male', '{"high_cholesterol"}', '{}', 'Mary Taylor', '+1234567800', true, true, 'en', NOW()),
(uuid_generate_v4(), 'premium2@email.com', crypt('patient123', gen_salt('bf')), 'patient', 'premium', NOW() + INTERVAL '1 year', 'Sophie', 'Martin', '+1234567801', '1988-09-25', 'female', '{"migraine"}', '{"aspirin"}', 'Pierre Martin', '+1234567802', true, true, 'km', NOW());

-- Sample prescriptions
WITH doctor_ids AS (
    SELECT id FROM users WHERE role = 'doctor' LIMIT 3
),
patient_ids AS (
    SELECT id FROM users WHERE role = 'patient' LIMIT 5
)
INSERT INTO prescriptions (id, patient_id, doctor_id, original_image_url, ocr_raw_text, ocr_corrected_text, ocr_confidence_score, prescription_date, pharmacy_name, status, created_at) VALUES
(uuid_generate_v4(), 
 (SELECT id FROM patient_ids OFFSET 0 LIMIT 1), 
 (SELECT id FROM doctor_ids OFFSET 0 LIMIT 1),
 'https://storage.example.com/prescriptions/sample1.jpg',
 'Amoxicillin 500mg\nTake 1 tablet 3 times daily\nFor 7 days\nWith food',
 'Amoxicillin 500mg\nTake 1 tablet 3 times daily\nFor 7 days\nWith food',
 0.95,
 CURRENT_DATE - INTERVAL '2 days',
 'City Pharmacy',
 'completed',
 NOW() - INTERVAL '2 days'),

(uuid_generate_v4(), 
 (SELECT id FROM patient_ids OFFSET 1 LIMIT 1), 
 (SELECT id FROM doctor_ids OFFSET 1 LIMIT 1),
 'https://storage.example.com/prescriptions/sample2.jpg',
 'Lisinopril 10mg\nTake 1 tablet once daily\nContinue as directed\nMorning dose',
 'Lisinopril 10mg\nTake 1 tablet once daily\nContinue as directed\nMorning dose',
 0.88,
 CURRENT_DATE - INTERVAL '5 days',
 'Health Plus Pharmacy',
 'completed',
 NOW() - INTERVAL '5 days'),

(uuid_generate_v4(), 
 (SELECT id FROM patient_ids OFFSET 2 LIMIT 1), 
 (SELECT id FROM doctor_ids OFFSET 2 LIMIT 1),
 'https://storage.example.com/prescriptions/sample3.jpg',
 'Metformin 850mg\nTake 1 tablet twice daily\nWith meals\n30 day supply',
 'Metformin 850mg\nTake 1 tablet twice daily\nWith meals\n30 day supply',
 0.92,
 CURRENT_DATE - INTERVAL '1 day',
 'Corner Drug Store',
 'completed',
 NOW() - INTERVAL '1 day');

-- Sample medications (linked to prescriptions)
WITH prescription_data AS (
    SELECT id, patient_id FROM prescriptions LIMIT 3
)
INSERT INTO medications (id, prescription_id, name, generic_name, strength, form, dosage, frequency, duration, instructions, created_at) VALUES
-- Prescription 1 medications
(uuid_generate_v4(), (SELECT id FROM prescription_data OFFSET 0 LIMIT 1), 'Amoxicillin', 'Amoxicillin', '500mg', 'tablet', '1 tablet', 'three times daily', '7 days', 'Take with food to reduce stomach upset', NOW()),

-- Prescription 2 medications  
(uuid_generate_v4(), (SELECT id FROM prescription_data OFFSET 1 LIMIT 1), 'Lisinopril', 'Lisinopril', '10mg', 'tablet', '1 tablet', 'once daily', 'ongoing', 'Take in the morning, monitor blood pressure', NOW()),

-- Prescription 3 medications
(uuid_generate_v4(), (SELECT id FROM prescription_data OFFSET 2 LIMIT 1), 'Metformin', 'Metformin', '850mg', 'tablet', '1 tablet', 'twice daily', '30 days', 'Take with meals, monitor blood sugar', NOW());

-- Sample doctor-patient relationships
WITH doctor_patient_pairs AS (
    SELECT 
        d.id as doctor_id, 
        p.id as patient_id,
        ROW_NUMBER() OVER () as rn
    FROM users d 
    CROSS JOIN users p 
    WHERE d.role = 'doctor' AND p.role = 'patient'
    LIMIT 6
)
INSERT INTO doctor_patient_relationships (id, doctor_id, patient_id, status, established_at, can_view_prescriptions, can_add_notes, created_at) VALUES
(uuid_generate_v4(), (SELECT doctor_id FROM doctor_patient_pairs WHERE rn = 1), (SELECT patient_id FROM doctor_patient_pairs WHERE rn = 1), 'active', NOW() - INTERVAL '30 days', true, true, NOW() - INTERVAL '30 days'),
(uuid_generate_v4(), (SELECT doctor_id FROM doctor_patient_pairs WHERE rn = 2), (SELECT patient_id FROM doctor_patient_pairs WHERE rn = 2), 'active', NOW() - INTERVAL '15 days', true, true, NOW() - INTERVAL '15 days'),
(uuid_generate_v4(), (SELECT doctor_id FROM doctor_patient_pairs WHERE rn = 3), (SELECT patient_id FROM doctor_patient_pairs WHERE rn = 3), 'active', NOW() - INTERVAL '7 days', true, false, NOW() - INTERVAL '7 days'),
(uuid_generate_v4(), (SELECT doctor_id FROM doctor_patient_pairs WHERE rn = 4), (SELECT patient_id FROM doctor_patient_pairs WHERE rn = 4), 'pending', NOW() - INTERVAL '2 days', true, true, NOW() - INTERVAL '2 days');

-- Sample medication reminders
WITH medication_data AS (
    SELECT m.id as medication_id, p.patient_id 
    FROM medications m 
    JOIN prescriptions p ON m.prescription_id = p.id 
    LIMIT 3
)
INSERT INTO medication_reminders (id, medication_id, patient_id, reminder_times, start_date, end_date, is_active, total_doses, created_at) VALUES
(uuid_generate_v4(), 
 (SELECT medication_id FROM medication_data OFFSET 0 LIMIT 1), 
 (SELECT patient_id FROM medication_data OFFSET 0 LIMIT 1),
 '{08:00,14:00,20:00}', 
 CURRENT_DATE, 
 CURRENT_DATE + INTERVAL '7 days', 
 true, 
 21, 
 NOW()),

(uuid_generate_v4(), 
 (SELECT medication_id FROM medication_data OFFSET 1 LIMIT 1), 
 (SELECT patient_id FROM medication_data OFFSET 1 LIMIT 1),
 '{08:00}', 
 CURRENT_DATE, 
 NULL, 
 true, 
 NULL, 
 NOW()),

(uuid_generate_v4(), 
 (SELECT medication_id FROM medication_data OFFSET 2 LIMIT 1), 
 (SELECT patient_id FROM medication_data OFFSET 2 LIMIT 1),
 '{08:00,20:00}', 
 CURRENT_DATE, 
 CURRENT_DATE + INTERVAL '30 days', 
 true, 
 60, 
 NOW());

-- Sample clinical notes
WITH doctor_patient_data AS (
    SELECT dpr.doctor_id, dpr.patient_id, p.id as prescription_id
    FROM doctor_patient_relationships dpr
    JOIN prescriptions p ON dpr.patient_id = p.patient_id
    WHERE dpr.status = 'active'
    LIMIT 3
)
INSERT INTO clinical_notes (id, doctor_id, patient_id, prescription_id, title, content, note_type, shared_with_patient, created_at) VALUES
(uuid_generate_v4(),
 (SELECT doctor_id FROM doctor_patient_data OFFSET 0 LIMIT 1),
 (SELECT patient_id FROM doctor_patient_data OFFSET 0 LIMIT 1),
 (SELECT prescription_id FROM doctor_patient_data OFFSET 0 LIMIT 1),
 'Antibiotic Treatment Follow-up',
 'Patient prescribed Amoxicillin for bacterial infection. Advised to complete full course even if symptoms improve. Monitor for any allergic reactions.',
 'follow-up',
 true,
 NOW()),

(uuid_generate_v4(),
 (SELECT doctor_id FROM doctor_patient_data OFFSET 1 LIMIT 1),
 (SELECT patient_id FROM doctor_patient_data OFFSET 1 LIMIT 1),
 (SELECT prescription_id FROM doctor_patient_data OFFSET 1 LIMIT 1),
 'Blood Pressure Management',
 'Started patient on Lisinopril 10mg daily. Blood pressure readings have been elevated. Patient advised to monitor BP at home and return in 2 weeks.',
 'observation',
 true,
 NOW());

-- Sample notifications
INSERT INTO notifications (id, user_id, type, title, message, is_read, created_at) VALUES
(uuid_generate_v4(), 
 (SELECT id FROM users WHERE role = 'patient' LIMIT 1), 
 'reminder', 
 'Medication Reminder', 
 'Time to take your Amoxicillin 500mg', 
 false, 
 NOW()),

(uuid_generate_v4(), 
 (SELECT id FROM users WHERE role = 'patient' OFFSET 1 LIMIT 1), 
 'alert', 
 'Doctor Message', 
 'Dr. Smith has added a note to your prescription', 
 false, 
 NOW() - INTERVAL '1 hour'),

(uuid_generate_v4(), 
 (SELECT id FROM users WHERE role = 'doctor' LIMIT 1), 
 'message', 
 'New Patient', 
 'Alice Wilson has shared a prescription with you', 
 true, 
 NOW() - INTERVAL '2 hours');

-- Sample usage analytics
INSERT INTO usage_analytics (id, user_id, event_type, event_data, device_type, platform, app_version, created_at) VALUES
(uuid_generate_v4(), 
 (SELECT id FROM users WHERE role = 'patient' LIMIT 1), 
 'prescription_scan', 
 '{"ocr_confidence": 0.95, "processing_time": 3.2}', 
 'mobile', 
 'android', 
 '1.0.0', 
 NOW() - INTERVAL '2 days'),

(uuid_generate_v4(), 
 (SELECT id FROM users WHERE role = 'patient' AND subscription_tier = 'premium' LIMIT 1), 
 'ai_report_generated', 
 '{"report_type": "medical_summary", "generation_time": 5.8}', 
 'mobile', 
 'ios', 
 '1.0.0', 
 NOW() - INTERVAL '1 day'),

(uuid_generate_v4(), 
 (SELECT id FROM users WHERE role = 'doctor' LIMIT 1), 
 'patient_prescription_viewed', 
 '{"prescription_id": "sample", "view_duration": 45}', 
 'tablet', 
 'ios', 
 '1.0.0', 
 NOW() - INTERVAL '3 hours');

COMMIT;