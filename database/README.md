# DasTern Database

PostgreSQL database for the DasTern Medical Prescription & Medication Management Platform.

## Quick Start (Docker)

```bash
# Start database
docker-compose up -d postgres

# Run all migrations
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/001_initial_schema.sql
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/002_enhanced_prescriptions.sql
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/003_family_and_reports.sql
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/004_onboarding_status.sql
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/005_role_profiles.sql
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/006_family_invitation_approval.sql
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/007_family_permissions.sql

# Load test data (optional)
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/seeds/test_users.sql
```

## Directory Structure

```
database/
├── migrations/           # Sequential schema changes
│   ├── 001_initial_schema.sql
│   ├── 002_enhanced_prescriptions.sql
│   ├── 003_family_and_reports.sql
│   ├── 004_onboarding_status.sql
│   ├── 005_role_profiles.sql
│   ├── 006_family_invitation_approval.sql
│   └── 007_family_permissions.sql
├── seeds/                # Test data
│   ├── development_data.sql
│   └── test_users.sql
├── functions/            # Custom SQL functions
│   └── user_functions.sql
├── schema.sql            # Legacy full schema
├── final-schema.sql      # Consolidated schema
└── Dockerfile
```

## Core Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts (patient, doctor, family_member, admin) |
| `patient_profiles` | Patient-specific data (DOB, blood type, allergies) |
| `doctor_profiles` | Doctor verification (license, hospital, specialty) |
| `family_member_profiles` | Family member relationship info |
| `prescriptions` | Prescription records with OCR/AI results |
| `medications` | Extracted medication details |
| `medication_reminders` | Scheduled medication reminders |
| `family_invitations` | Patient-to-family connection codes |
| `family_connection_requests` | Pending family approval requests |

## Enums

```sql
user_role: 'patient' | 'doctor' | 'family_member' | 'admin'
onboarding_status: 'pending' | 'role_selected' | 'profile_pending' | 'active'
subscription_tier: 'free' | 'premium'
prescription_status: 'processing' | 'completed' | 'error' | 'archived'
```

## Migrations Summary

| # | Migration | Description |
|---|-----------|-------------|
| 001 | Initial Schema | Users, prescriptions, medications, reminders |
| 002 | Enhanced Prescriptions | OCR confidence, doctor fields |
| 003 | Family & Reports | Family members, AI reports |
| 004 | Onboarding Status | User onboarding flow tracking |
| 005 | Role Profiles | Separate profile tables per role |
| 006 | Family Approval | Connection request workflow |
| 007 | Family Permissions | JSONB permissions for family access |

## Common Commands

```bash
# Connect to database
docker exec -it dastern-postgres psql -U dastern -d dastern_db

# Check tables
\dt

# Describe table
\d users

# Check user roles
SELECT id, email, role, onboarding_status FROM users;

# Check family connections
SELECT * FROM family_invitations WHERE status = 'accepted';
```

## Key Features

- **Role-based access**: Patient, Doctor, Family Member, Admin
- **Onboarding flow**: Tracks user registration progress
- **Family system**: Invitation codes with approval workflow
- **Permissions**: JSONB-based granular family access control
- **Audit logging**: Tracks all data access
