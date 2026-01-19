# DasTern V2 Database Documentation

## Overview

This directory contains the complete database schema and related files for the DasTern V2 Medical Prescription OCR & AI Assistance Platform. The database is designed using PostgreSQL with a focus on security, performance, and scalability.

## Database Structure

### Core Tables

#### User Management
- **users** - Core user information (patients, doctors, admins)
- **user_sessions** - JWT token management and session tracking
- **user_subscriptions** - Premium subscription management
- **subscription_plans** - Available subscription tiers and features

#### Prescription Management
- **prescriptions** - Core prescription data with OCR and AI results
- **medications** - Individual medications extracted from prescriptions
- **medication_reminders** - User-configured medication reminders
- **medication_reminder_logs** - Tracking of reminder actions

#### Doctor-Patient Workflow
- **doctor_patient_relationships** - Doctor-patient connections
- **clinical_notes** - Doctor notes and observations

#### AI Features (Premium)
- **ai_chat_conversations** - AI chat sessions
- **ai_chat_messages** - Individual chat messages
- **ai_reports** - Generated AI reports and analysis

#### System & Analytics
- **notifications** - System notifications and alerts
- **usage_analytics** - User behavior and feature usage tracking
- **audit_logs** - Security and compliance audit trail
- **payment_transactions** - Payment processing records

## Files Structure

```
database/
├── schema.sql                 # Complete database schema
├── migrations/
│   └── 001_initial_schema.sql # Initial migration
├── seeds/
│   └── development_data.sql   # Sample data for development
├── functions/
│   └── user_functions.sql     # Custom database functions
└── README.md                  # This documentation
```

## Setup Instructions

### 1. Initial Database Setup

```bash
# Create database
createdb dastern_v2

# Run initial schema
psql -d dastern_v2 -f database/schema.sql

# Or use migration approach
psql -d dastern_v2 -f database/migrations/001_initial_schema.sql
```

### 2. Load Development Data

```bash
# Load sample data for development
psql -d dastern_v2 -f database/seeds/development_data.sql
```

### 3. Install Custom Functions

```bash
# Install utility functions
psql -d dastern_v2 -f database/functions/user_functions.sql
```

## Key Features

### 1. Security Features

#### Row Level Security (RLS)
- Prescriptions are only accessible to the patient, their doctors, or admins
- Clinical notes are restricted to the authoring doctor and patient
- AI chat conversations are private to the user

#### Data Encryption
- Passwords are hashed using bcrypt
- Sensitive data fields are designed for encryption at rest
- All connections use TLS encryption

#### Audit Trail
- All data access and modifications are logged
- User sessions are tracked with device and IP information
- Payment transactions are fully auditable

### 2. Performance Optimizations

#### Indexes
- Strategic indexes on frequently queried columns
- Composite indexes for complex queries
- Partial indexes for filtered queries

#### Views
- Pre-computed views for common queries
- User profile view with subscription information
- Prescription summary view with medication counts

#### Functions
- Custom functions for business logic
- Efficient subscription validation
- Automated cleanup procedures

### 3. Business Logic

#### Subscription Management
- Free tier limitations (10 prescriptions max)
- Premium feature access control
- Usage tracking and limits

#### Doctor-Patient Relationships
- Invitation-based connection system
- Granular permission controls
- Relationship status management

#### Medication Reminders
- Flexible scheduling system
- Comprehensive tracking and logging
- Statistics and adherence monitoring

## Data Types and Enums

### Custom Types
```sql
user_role: 'patient', 'doctor', 'admin'
subscription_tier: 'free', 'premium'
prescription_status: 'processing', 'completed', 'error', 'archived'
relationship_status: 'pending', 'active', 'inactive', 'blocked'
notification_type: 'reminder', 'alert', 'message', 'system'
payment_status: 'pending', 'completed', 'failed', 'refunded'
```

## Sample Queries

### Get User's Prescriptions with Medications
```sql
SELECT 
    p.id,
    p.prescription_date,
    p.pharmacy_name,
    p.status,
    array_agg(m.name || ' ' || m.strength) as medications
FROM prescriptions p
LEFT JOIN medications m ON p.id = m.prescription_id
WHERE p.patient_id = $1
GROUP BY p.id, p.prescription_date, p.pharmacy_name, p.status
ORDER BY p.created_at DESC;
```

### Check Premium Feature Access
```sql
SELECT user_has_premium_subscription($1) as has_premium,
       can_make_ai_request($1) as can_use_ai;
```

### Get Active Medication Reminders
```sql
SELECT * FROM get_active_reminders($1);
```

## Maintenance Tasks

### Regular Cleanup
```sql
-- Clean expired sessions (run daily)
SELECT cleanup_expired_sessions();

-- Archive old prescriptions (run monthly)
SELECT archive_old_prescriptions(365);
```

### Statistics and Monitoring
```sql
-- User statistics
SELECT * FROM get_user_statistics();

-- Prescription statistics
SELECT * FROM get_prescription_statistics();
```

## Migration Strategy

### Adding New Columns
1. Create migration file in `migrations/` directory
2. Use `ALTER TABLE` statements with default values
3. Update application code to handle new fields
4. Test thoroughly in development environment

### Schema Changes
1. Always backup production data before migrations
2. Use transactions for atomic changes
3. Test rollback procedures
4. Monitor performance after changes

## Security Considerations

### Data Protection
- Never store plain text passwords
- Encrypt sensitive medical data
- Use parameterized queries to prevent SQL injection
- Implement proper access controls

### Compliance
- Log all access to medical data
- Implement data retention policies
- Provide data export capabilities for user requests
- Ensure GDPR compliance features

### Monitoring
- Monitor failed login attempts
- Track unusual data access patterns
- Alert on bulk data operations
- Regular security audits

## Performance Monitoring

### Key Metrics to Monitor
- Query execution times
- Index usage statistics
- Connection pool utilization
- Database size growth
- Slow query identification

### Optimization Tips
- Regular VACUUM and ANALYZE operations
- Monitor and optimize slow queries
- Consider partitioning for large tables
- Use connection pooling
- Implement proper caching strategies

## Backup and Recovery

### Backup Strategy
- Daily full backups
- Continuous WAL archiving
- Test restore procedures regularly
- Store backups in multiple locations

### Recovery Procedures
- Point-in-time recovery capability
- Documented recovery steps
- Regular disaster recovery testing
- RTO/RPO targets defined

## Development Guidelines

### Naming Conventions
- Tables: plural nouns (users, prescriptions)
- Columns: snake_case (first_name, created_at)
- Indexes: idx_table_column format
- Functions: descriptive names with underscores

### Best Practices
- Always use transactions for multi-table operations
- Include created_at and updated_at timestamps
- Use UUIDs for primary keys
- Implement proper foreign key constraints
- Add appropriate check constraints for data validation

This database design provides a solid foundation for the DasTern V2 platform, balancing functionality, security, and performance requirements.