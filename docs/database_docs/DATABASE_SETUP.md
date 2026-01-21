# 🗄️ DasTern Database Setup Guide - Fedora

Complete guide for setting up PostgreSQL for DasTern using **CLI or GUI** options.

---

## 📋 Quick Start (Choose One)

### 🐳 **Option 1: Docker Compose (EASIEST - Recommended)**

```bash
# Make script executable
chmod +x setup-database.sh

# Run interactive setup
./setup-database.sh
# Select option 1

# Or use Docker directly
docker-compose up -d postgres

# Wait a few seconds, then verify
docker-compose exec postgres psql -U dastern -d dastern -c "SELECT version();"
```

**Pros:**
- No system-wide installation
- Easy cleanup (just stop the container)
- Portable and reproducible

---

### 🖥️ **Option 2: Native PostgreSQL Installation**

```bash
# Make script executable
chmod +x setup-database.sh

# Run interactive setup
./setup-database.sh
# Select option 2

# Or manual steps:
sudo dnf install postgresql postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Pros:**
- Runs system-wide
- Direct psql access
- Better for development

---

## 🔧 Manual CLI Setup (Step-by-Step)

### **1. Install PostgreSQL on Fedora**

```bash
# Install PostgreSQL server and utilities
sudo dnf install -y postgresql postgresql-server postgresql-contrib

# Initialize the database cluster
sudo postgresql-setup initdb

# Start the service
sudo systemctl start postgresql

# Enable on boot
sudo systemctl enable postgresql

# Verify it's running
sudo systemctl status postgresql
```

### **2. Create Database User and Database**

```bash
# Switch to postgres user and open psql
sudo -u postgres psql

# Inside psql prompt, run these commands:
```

```sql
-- Create the dastern user
CREATE USER dastern WITH PASSWORD 'dastern_secure_password_2026';

-- Create the dastern database
CREATE DATABASE dastern OWNER dastern;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE dastern TO dastern;

-- Exit psql
\q
```

### **3. Configure PostgreSQL Authentication**

```bash
# Backup the original config
sudo cp /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.backup

# Edit the authentication config
sudo nano /var/lib/pgsql/data/pg_hba.conf
```

**Find this line:**
```
local   all             all                                     peer
```

**Replace with:**
```
local   all             all                                     md5
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### **4. Reload PostgreSQL Configuration**

```bash
sudo systemctl reload postgresql
```

### **5. Test Connection**

```bash
# Test with password authentication
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "SELECT version();"

# Should output PostgreSQL version info
```

### **6. Import Database Schema**

```bash
# From the DasTern project directory
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost < database/schema.sql

# Check if successful (should see "CREATE TABLE", "CREATE INDEX", etc.)
```

### **7. Verify Schema Was Imported**

```bash
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "\dt"

# Should list all tables created
```

---

## 🎨 DBeaver GUI Setup

### **Step 1: Install DBeaver (if not installed)**

```bash
# Install DBeaver Community Edition
sudo dnf install dbeaver-community
```

### **Step 2: Create Connection in DBeaver**

1. **Open DBeaver**
2. Click **Database** → **New Database Connection**
3. Select **PostgreSQL** → Click **Next**

### **Step 3: Configure Connection**

Fill in these details:

| Field | Value |
|-------|-------|
| **Server Host** | localhost |
| **Port** | 5432 |
| **Database** | dastern |
| **Username** | dastern |
| **Password** | dastern_secure_password_2026 |
| **Save password locally** | ✓ Checked |

### **Step 4: Test Connection**

- Click **Test Connection** button
- You should see a green checkmark: ✅ "Connected"
- If it fails, verify credentials above

### **Step 5: Finish**

- Click **Finish**
- Connection appears in left panel under "Database"

### **Step 6: Import Schema**

1. Expand **dastern** database in left panel
2. Right-click → **SQL Editor** → **Open SQL Script**
3. Select file: `database/schema.sql`
4. Press **Ctrl + Enter** or click Execute button
5. Check **Console** tab at bottom for any errors

---

## 🐛 Troubleshooting

### **Error: "Access denied for user 'dastern'@'localhost' (using password: YES)"**

**Solution:**
```bash
# 1. Check if PostgreSQL is running
sudo systemctl status postgresql

# 2. Verify user exists
sudo -u postgres psql -c "SELECT usename FROM pg_user WHERE usename='dastern';"

# 3. Reset password
sudo -u postgres psql -c "ALTER USER dastern WITH PASSWORD 'dastern_secure_password_2026';"

# 4. Check pg_hba.conf authentication method
sudo grep "^local" /var/lib/pgsql/data/pg_hba.conf

# 5. Reload config
sudo systemctl reload postgresql
```

### **Error: "database "dastern" does not exist"**

```bash
# Create the database
sudo -u postgres createdb -O dastern dastern

# Or via psql:
sudo -u postgres psql -c "CREATE DATABASE dastern OWNER dastern;"
```

### **Error: "FATAL: Ident authentication failed for user"**

**Solution:** Edit pg_hba.conf as shown above (change `peer` to `md5`)

### **Error: "Port 5432 already in use"** (Docker users)

```bash
# Check what's using the port
sudo ss -tlnp | grep 5432

# Stop the process or use different port in docker-compose:
# Change "5432:5432" to "5433:5432"
```

### **Database Connection Timeout**

```bash
# 1. Check if postgres is listening
sudo ss -tlnp | grep postgres

# 2. Check listen_addresses in postgresql.conf
sudo grep "listen_addresses" /var/lib/pgsql/data/postgresql.conf

# 3. Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# 1. PostgreSQL service is running
sudo systemctl status postgresql

# 2. User dastern exists
sudo -u postgres psql -c "SELECT usename FROM pg_user WHERE usename='dastern';"

# 3. Database dastern exists
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname='dastern';"

# 4. Can connect with password
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "SELECT 1;"

# 5. Schema was imported
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "\dt"
```

All commands should execute without errors.

---

## 📝 Environment Variables

Save these to your `.env` file for the application:

```bash
# Database Configuration
DB_USER=dastern
DB_PASSWORD=dastern_secure_password_2026
DB_NAME=dastern
DB_PORT=5432
DATABASE_URL=postgresql://dastern:dastern_secure_password_2026@localhost:5432/dastern
```

---

## 🚀 Next Steps

After database is set up:

1. **Start Docker services:**
   ```bash
   docker-compose up
   ```

2. **Access services:**
   - Backend: http://localhost:3000
   - OCR Service: http://localhost:8000
   - AI LLM Service: http://localhost:8001

3. **Connect DBeaver to monitor:**
   - See GUI Setup section above

---

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `sudo systemctl start postgresql` | Start service |
| `sudo systemctl stop postgresql` | Stop service |
| `sudo systemctl restart postgresql` | Restart service |
| `sudo systemctl status postgresql` | Check status |
| `sudo -u postgres psql` | Enter PostgreSQL |
| `\dt` | List tables in psql |
| `\q` | Exit psql |
| `psql -U dastern -d dastern` | Connect as dastern user |

---

**Need help?** Check the troubleshooting section above! 🆘
