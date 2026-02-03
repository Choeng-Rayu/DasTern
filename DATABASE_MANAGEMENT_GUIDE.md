# 📚 DasTern Database Management Guide

## 1. 🔌 Accessing PostgreSQL in Docker

### Quick Access Methods

#### Method 1: Interactive psql shell
```bash
# Connect to database
docker exec -it dastern-postgres psql -U dastern -d dastern

# Common commands inside psql:
\dt                           # List all tables
\d table_name                 # Describe a table
\du                           # List users
\l                            # List databases
\q                            # Quit

# Example queries:
SELECT * FROM users LIMIT 5;
SELECT COUNT(*) FROM prescriptions;
```

#### Method 2: Execute single SQL command
```bash
docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT * FROM users;"
```

#### Method 3: Execute SQL file
```bash
docker exec -i dastern-postgres psql -U dastern -d dastern < your_script.sql
```

#### Method 4: From host machine (requires psql installed)
```bash
psql -h localhost -p 5432 -U dastern -d dastern
# Password: dastern_capstone_2
```

---

## 2. 🔄 Database Migrations in Docker

### How Auto-Update Works

Your `docker-compose.yml` has this configuration:
```yaml
volumes:
  - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
  - ./database/migrations:/docker-entrypoint-initdb.d/migrations
```

**Important:** Files in `/docker-entrypoint-initdb.d/` only run **once** when the database is first initialized!

### Migration Strategies

#### Strategy 1: Use the Migration Script (Recommended)
```bash
# Run all migrations
./migrate-database.sh

# Or manually run specific migration
docker exec -i dastern-postgres psql -U dastern -d dastern < database/migrations/002_add_columns.sql
```

#### Strategy 2: Reset Database (⚠️ Deletes all data!)
```bash
# Stop containers and remove volumes
docker compose down -v

# Restart (will re-run schema.sql)
docker compose up -d

# Re-seed test data
docker exec -i dastern-postgres psql -U dastern -d dastern < database/seeds/test_users.sql
```

#### Strategy 3: Create Migration Files

Create numbered migration files in `database/migrations/`:

**Example: `database/migrations/002_add_profile_fields.sql`**
```sql
-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;

-- Create index
CREATE INDEX IF NOT EXISTS idx_users_avatar ON users(avatar_url);
```

Then run:
```bash
./migrate-database.sh
```

---

## 3. 🐛 Common Issues & Solutions

### Issue 1: Foreign Key Constraint Error
**Error:** `Key (patient_id)=(00000000-0000-0000-0000-000000000000) is not present in table "users"`

**Solution:** Create test users first
```bash
docker exec -i dastern-postgres psql -U dastern -d dastern < database/seeds/test_users.sql
```

**Test Users Created:**
- Patient: `patient@test.com` (ID: `00000000-0000-0000-0000-000000000000`)
- Doctor: `doctor@test.com` (ID: `00000000-0000-0000-0000-000000000001`)
- Patient 2: `patient2@test.com` (ID: `11111111-1111-1111-1111-111111111111`)
- Password: `password123`

### Issue 2: Database Already Exists
If you see errors like "relation already exists", the database was already initialized.

**Options:**
1. Drop specific table: 
   ```sql
   DROP TABLE IF EXISTS table_name CASCADE;
   ```
2. Reset database: 
   ```bash
   docker compose down -v && docker compose up -d
   ```

### Issue 3: Connection Refused
**Check if container is running:**
```bash
docker ps | grep postgres
```

**Check logs:**
```bash
docker logs dastern-postgres
```

**Restart:**
```bash
docker compose restart postgres
```

---

## 4. 🔧 Useful Database Commands

### Check Database Status
```bash
# Connection test
docker exec dastern-postgres pg_isready -U dastern

# Database size
docker exec -it dastern-postgres psql -U dastern -d dastern -c "
SELECT 
    pg_size_pretty(pg_database_size('dastern')) as size,
    pg_database_size('dastern') as bytes;
"

# Table sizes
docker exec -it dastern-postgres psql -U dastern -d dastern -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

### Backup & Restore
```bash
# Backup
docker exec dastern-postgres pg_dump -U dastern dastern > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i dastern-postgres psql -U dastern -d dastern < backup_20260122.sql
```

### View Data
```bash
# Count records in all tables
docker exec -it dastern-postgres psql -U dastern -d dastern -c "
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
"

# Recent prescriptions
docker exec -it dastern-postgres psql -U dastern -d dastern -c "
SELECT 
    id,
    patient_id,
    status,
    ocr_confidence_score,
    created_at
FROM prescriptions
ORDER BY created_at DESC
LIMIT 5;
"
```

---

## 5. 📝 Creating Seed Data

### Test Users (Already Created)
Location: `database/seeds/test_users.sql`

### Add More Seed Data

**Example: `database/seeds/sample_prescriptions.sql`**
```sql
-- Sample prescriptions for testing
INSERT INTO prescriptions (
    patient_id,
    original_image_url,
    ocr_raw_text,
    ocr_corrected_text,
    ocr_confidence_score,
    status
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    'https://example.com/prescription1.jpg',
    'Amoxicillin 500mg\nTake 1 tablet twice daily',
    'Amoxicillin 500mg\nTake 1 tablet twice daily',
    0.95,
    'completed'
)
RETURNING id;
```

**Run it:**
```bash
docker exec -i dastern-postgres psql -U dastern -d dastern < database/seeds/sample_prescriptions.sql
```

---

## 6. 🚀 Quick Commands Cheatsheet

```bash
# Start database
docker compose up -d postgres

# Stop database
docker compose stop postgres

# View logs
docker logs -f dastern-postgres

# Access database
docker exec -it dastern-postgres psql -U dastern -d dastern

# Run migration
./migrate-database.sh

# Seed test users
docker exec -i dastern-postgres psql -U dastern -d dastern < database/seeds/test_users.sql

# Reset database (⚠️ deletes data)
docker compose down -v && docker compose up -d

# Backup
docker exec dastern-postgres pg_dump -U dastern dastern > backup.sql

# Check running services
docker compose ps
```

---

## 7. 🔐 Database Credentials

From your `.env`:
```env
DB_USER=dastern
DB_PASSWORD=dastern_capstone_2
DB_NAME=dastern
DB_PORT=5432
DATABASE_URL=postgresql://dastern:dastern_capstone_2@postgres:5432/dastern
```

**Connection String for External Tools:**
```
Host: localhost
Port: 5432
Database: dastern
Username: dastern
Password: dastern_capstone_2
```

---

## 8. 📊 Monitoring

### Check Database Health
```bash
docker exec dastern-postgres pg_isready -U dastern
```

### Monitor Active Connections
```bash
docker exec -it dastern-postgres psql -U dastern -d dastern -c "
SELECT 
    datname,
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'dastern';
"
```

### Check Database Performance
```bash
docker exec -it dastern-postgres psql -U dastern -d dastern -c "
SELECT 
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
"
```

---

## 9. ⚠️ Important Notes

1. **Automatic Schema Loading**: Only happens on **first startup** when volume is empty
2. **Migrations**: Must be run manually using `./migrate-database.sh`
3. **Test Users**: Always run seed data after resetting database
4. **Backups**: Create backups before major changes
5. **Foreign Keys**: Ensure referenced records exist before inserting

---

## 10. 🎯 Next Steps

1. ✅ Test users created - foreign key error fixed!
2. Try uploading an image at http://localhost:3000
3. Check the prescriptions table:
   ```bash
   docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT * FROM prescriptions;"
   ```
4. View extracted medications:
   ```bash
   docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT * FROM medications;"
   ```

---

**Need help? Check the logs:**
```bash
docker compose logs -f backend
docker compose logs -f postgres
```
