# Database Migration Guide for DasTern

## Overview

The database schema is **built into the Docker image** using COPY, not volume mounts. This provides:
- ✅ Better security and permissions
- ✅ Consistent deployments
- ✅ No host file permission issues

## Initial Setup

The initial schema is automatically loaded when the PostgreSQL container is first created:
- File: `database/final-schema.sql`
- Location in container: `/docker-entrypoint-initdb.d/01-schema.sql`
- Runs: Only on first initialization (when volume is empty)

## Running Migrations

### Method 1: Using the Migration Script (Recommended)

```bash
# Apply a migration file
./database/migrate.sh database/migrations/004_new_feature.sql
```

The script automatically:
- Detects if using Docker or direct connection
- Uses appropriate connection method
- Applies the migration
- Reports success/failure

### Method 2: Direct Docker Exec

```bash
# Copy migration to container and execute
docker exec -i dastern-postgres psql -U dastern -d dastern < database/migrations/004_new_feature.sql

# Or connect interactively
docker exec -it dastern-postgres psql -U dastern -d dastern
```

### Method 3: Using psql from Host

```bash
# If you have psql installed locally
PGPASSWORD=dastern_secure_password_2026 psql -h localhost -p 5432 -U dastern -d dastern -f database/migrations/004_new_feature.sql
```

## Creating New Migrations

### Step 1: Create Migration File

```bash
# Create new migration file
nano database/migrations/004_my_new_feature.sql
```

Example migration:
```sql
-- Migration: Add notification preferences
-- Date: 2026-01-26
-- Author: Your Name

BEGIN;

-- Add new column
ALTER TABLE users 
ADD COLUMN notification_enabled BOOLEAN DEFAULT true;

-- Create index
CREATE INDEX idx_users_notifications 
ON users(notification_enabled) 
WHERE notification_enabled = true;

COMMIT;
```

### Step 2: Apply Migration

```bash
./database/migrate.sh database/migrations/004_my_new_feature.sql
```

### Step 3: Update Schema Documentation

Update `database/final-schema.sql` with the changes for future deployments.

## Updating the Base Schema

If you need to update the base schema in the Docker image:

### Step 1: Update Schema File

```bash
# Edit the base schema
nano database/final-schema.sql
```

### Step 2: Rebuild PostgreSQL Image

```bash
# Rebuild the postgres service
docker compose build postgres

# Stop and remove the old container and volume
docker compose down
docker volume rm dastern_postgres_data

# Start fresh with new schema
docker compose up -d
```

⚠️ **WARNING**: This will **DELETE ALL DATA**. Use migrations for existing databases!

## Migration Best Practices

### 1. Always Use Transactions

```sql
BEGIN;
-- Your changes here
COMMIT;
```

### 2. Make Migrations Reversible

Create both UP and DOWN migrations:
```sql
-- UP Migration (004_add_feature.sql)
BEGIN;
ALTER TABLE users ADD COLUMN new_field VARCHAR(255);
COMMIT;

-- DOWN Migration (004_add_feature_rollback.sql)
BEGIN;
ALTER TABLE users DROP COLUMN new_field;
COMMIT;
```

### 3. Test Migrations

```bash
# Test on development database first
./database/migrate.sh database/migrations/test_004.sql

# Verify the changes
docker exec -it dastern-postgres psql -U dastern -d dastern -c "\d users"
```

### 4. Document Migrations

Add comments to your migration files:
```sql
-- Migration: 004_add_notification_system
-- Date: 2026-01-26
-- Author: Team Name
-- Description: Adds notification preferences and history tables
```

## Troubleshooting

### Migration Failed

```bash
# Check PostgreSQL logs
docker compose logs postgres

# Connect to database to inspect
docker exec -it dastern-postgres psql -U dastern -d dastern

# Check current schema
\dt
\d table_name
```

### Reset Database

```bash
# Complete reset (deletes all data)
docker compose down
docker volume rm dastern_postgres_data
docker compose build postgres
docker compose up -d postgres
```

### Backup Before Migration

```bash
# Create backup
docker exec dastern-postgres pg_dump -U dastern dastern > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup if needed
docker exec -i dastern-postgres psql -U dastern -d dastern < backup_20260126_143000.sql
```

## Environment Variables

Set these in your `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=dastern
DB_PASSWORD=dastern_secure_password_2026
DB_NAME=dastern
```

## Migration Tracking

Consider creating a migrations table to track applied migrations:

```sql
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- After each migration, record it:
INSERT INTO schema_migrations (version, description) 
VALUES ('004', 'Added notification system');
```

## Quick Reference

```bash
# Apply migration
./database/migrate.sh path/to/migration.sql

# Connect to database
docker exec -it dastern-postgres psql -U dastern -d dastern

# View tables
docker exec dastern-postgres psql -U dastern -d dastern -c "\dt"

# Backup
docker exec dastern-postgres pg_dump -U dastern dastern > backup.sql

# Restore
docker exec -i dastern-postgres psql -U dastern -d dastern < backup.sql

# View logs
docker compose logs -f postgres

# Rebuild with new schema (DESTRUCTIVE)
docker compose down && docker volume rm dastern_postgres_data && docker compose build postgres && docker compose up -d
```
