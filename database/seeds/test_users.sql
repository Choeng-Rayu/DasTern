-- Seed Data for Testing
-- Run this to populate test data

-- Create test users
INSERT INTO users (
    id,
    email,
    password_hash,
    role,
    first_name,
    last_name,
    is_active,
    email_verified
) VALUES 
-- Test Patient (UUID: 00000000-0000-0000-0000-000000000000)
(
    '00000000-0000-0000-0000-000000000000',
    'patient@test.com',
    crypt('password123', gen_salt('bf')),
    'patient',
    'Test',
    'Patient',
    true,
    true
),
-- Test Doctor
(
    '00000000-0000-0000-0000-000000000001',
    'doctor@test.com',
    crypt('password123', gen_salt('bf')),
    'doctor',
    'Dr. John',
    'Smith',
    true,
    true
),
-- Another Test Patient
(
    '11111111-1111-1111-1111-111111111111',
    'patient2@test.com',
    crypt('password123', gen_salt('bf')),
    'patient',
    'Jane',
    'Doe',
    true,
    true
)
ON CONFLICT (id) DO NOTHING;

-- Create test doctor-patient relationship
INSERT INTO doctor_patient_relationships (
    doctor_id,
    patient_id,
    status,
    established_at
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000000',
    'active',
    NOW()
)
ON CONFLICT (doctor_id, patient_id) DO NOTHING;

-- Display created users
SELECT 
    id,
    email,
    role,
    first_name || ' ' || last_name as name,
    is_active
FROM users
WHERE email LIKE '%@test.com'
ORDER BY created_at;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Test users created successfully!';
    RAISE NOTICE '   Patient: patient@test.com (password: password123)';
    RAISE NOTICE '   Patient ID: 00000000-0000-0000-0000-000000000000';
    RAISE NOTICE '   Doctor: doctor@test.com (password: password123)';
END $$;
