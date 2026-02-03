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

# DasTern Database — brief relational architecture

Purpose
- PostgreSQL schema for DasTern: prescription OCR ingest, medication extraction, reminders, family/doctor sharing, AI features and billing.
- This README summarizes tables, core relationships and feature flows so reviewers can grasp the model before deep dives.

Quick start (Docker)
```bash
# Start DB
docker-compose up -d postgres

# Run all migrations (example)
docker exec -i dastern-postgres psql -U dastern -d dastern_db < database/migrations/001_initial_schema.sql
# ...run subsequent migration files in order...
```

Core concept
- Single canonical users table. Other domain entities reference users by role (patient, doctor, family_member, admin).
- Prescriptions are the central document entity. OCR → medications → reminders → adherence logs.
- Templates, queues, analytics, notifications and audit logs provide operability and observability.

Tables (essential columns + short description)
- users (id, email, role, first_name, last_name, is_active, created_at)
  - Central actor table for patients, doctors, family, admins.

- user_sessions (id, user_id → users, refresh_token, expires_at)
  - Stores refresh tokens / sessions.

- subscription_plans (id, name, tier, price_monthly)
  - Catalog of plans (free/premium).

- user_subscriptions (id, user_id → users, plan_id → subscription_plans, status, current_period_end)
  - User's active subscription record.

- payment_transactions (id, user_id → users, subscription_id → user_subscriptions, amount, status, processed_at)
  - Payment history.

- prescriptions (id, patient_id → users, doctor_id → users, original_image_url, status, prescription_date, ocr_confidence_score, ai_confidence_score)
  - Uploaded prescription image + OCR/AI metadata.

- prescription_processing_queue (id, prescription_id → prescriptions, status, priority, started_at, completed_at)
  - Async worker queue for OCR/AI processing.

- medications (id, prescription_id → prescriptions, sequence_number, name, strength, form)
  - Medicines parsed out of a prescription.

- medication_schedule_templates (id, name, morning_time, noon_time, evening_time, night_time, is_default)
  - Reusable reminder presets (can be system or user-owned).

- medication_reminders (id, medication_id → medications, patient_id → users, time_slot, scheduled_time, start_date, end_date, is_active, template_id?)
  - Scheduled reminders for a medication. (Recommended: include template_id + template_snapshot for traceability.)

- medication_reminder_logs (id, reminder_id → medication_reminders, medication_id → medications, patient_id → users, scheduled_date, actual_time, status)
  - History of reminder events (taken/missed/snoozed).

- doctor_patient_relationships (id, doctor_id → users, patient_id → users, status, permissions)
  - Links doctors with patients and stores permissions.

- family_relationships (id, patient_id → users, family_member_id → users, relationship_type, status, permissions)
  - Family access and invitation lifecycle.

- clinical_notes (id, doctor_id → users, patient_id → users, prescription_id → prescriptions, title, content)
  - Doctor notes (can be shared/hidden).

- ai_chat_conversations (id, user_id → users, prescription_id → prescriptions, title, created_at)
  - AI chat sessions (premium feature).

- ai_chat_messages (id, conversation_id → ai_chat_conversations, message_type, content, ai_confidence_score)
  - Messages within an AI conversation.

- ai_reports (id, prescription_id → prescriptions, user_id → users, report_type, summary, ai_confidence_score)
  - Generated AI analysis reports tied to prescriptions/users.

- notifications (id, user_id → users, type, title, message, is_read, created_at)
  - Push/email/in-app notifications.

- usage_analytics (id, user_id → users, event_type, event_data, created_at)
  - Telemetry/events for monitoring and metrics.

- audit_logs (id, user_id → users, action, resource_type, resource_id, created_at)
  - Security and compliance audit trail.

Primary relationships (textual ERD)
- users 1..* → prescriptions (patient_id)
- prescriptions 1..* → medications
- prescriptions 1..1 → prescription_processing_queue entries (many-to-one possible for retries/history)
- medications 1..* → medication_reminders
- medication_reminders 1..* → medication_reminder_logs
- users 1..* → user_sessions, user_subscriptions, payment_transactions, notifications, usage_analytics, audit_logs
- users ↔ users via doctor_patient_relationships and family_relationships (both reference users twice)
- ai_chat_conversations → users and optionally → prescriptions; ai_chat_messages → ai_chat_conversations
- ai_reports → users and prescriptions

Feature flows (tables required)
- Auth & account: users, user_sessions, notifications, audit_logs
- Subscription & billing: subscription_plans, user_subscriptions, payment_transactions, notifications
- Prescription ingest (OCR): users, prescriptions, prescription_processing_queue
- Medication extraction: prescriptions, medications
- Reminder lifecycle: medications, medication_schedule_templates, medication_reminders, medication_reminder_logs, notifications
- Doctor workflow: users, doctor_patient_relationships, clinical_notes, prescriptions
- Family sharing: users, family_relationships, notifications, medication_reminders (viewing)
- AI features: users, ai_chat_conversations, ai_chat_messages, ai_reports, prescriptions
- Operations: prescription_processing_queue, usage_analytics, audit_logs

Design notes / recommendations
- Templates: keep template_id FK on medication_reminders and also store template_snapshot JSONB at creation for immutability.
- Permissions: prefer explicit boolean columns for frequent checks plus JSONB for extensible rules.
- Indexes: add indexes on foreign keys and on time fields (prescription.created_at, reminder.next_reminder_at) for scheduler performance.
- Audit: write concise audit events for sensitive operations (view prescription, modify reminder).
- Queue: use FOR UPDATE SKIP LOCKED pattern to pick jobs safely.

Useful example queries
- Recent prescriptions for a patient:
  SELECT * FROM prescriptions WHERE patient_id = '<user_id>' ORDER BY created_at DESC LIMIT 20;
- Active reminders due soon:
  SELECT * FROM medication_reminders WHERE patient_id = '<user_id>' AND is_active = TRUE AND next_reminder_at < NOW() + INTERVAL '1 hour';

Where to read deeper
- Migrations: database/migrations/*.sql — authoritative schema changes.
- Functions: database/functions/user_functions.sql — DB helper logic.
- Seeds: database/seeds/* — example data for testing.

If you want, I will:
- produce a one-page simplified ERD SVG for the presentation, or
- generate the ALTER scripts to add template_id + template_snapshot and appropriate indexes. Which do you prefer?
