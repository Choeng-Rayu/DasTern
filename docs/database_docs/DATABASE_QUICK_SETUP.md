# ⚡ Database Setup - Quick Reference Card

## 🚀 FASTEST WAY - One Command

### Option A: Docker (Recommended)
```bash
cd ~/DasTern
docker-compose up -d postgres
sleep 5
docker-compose exec postgres psql -U dastern -d dastern -c "SELECT version();"
```

### Option B: Interactive Script
```bash
cd ~/DasTern
./setup-database.sh
# Follow the prompts
```

---

## 🖥️ Manual CLI - 60 Seconds

```bash
# 1. Install PostgreSQL
sudo dnf install -y postgresql postgresql-server postgresql-contrib

# 2. Initialize & Start
sudo postgresql-setup initdb
sudo systemctl start postgresql

# 3. Create user & database
sudo -u postgres psql << EOF
CREATE USER dastern WITH PASSWORD 'dastern_secure_password_2026';
CREATE DATABASE dastern OWNER dastern;
GRANT ALL PRIVILEGES ON DATABASE dastern TO dastern;
\q
EOF

# 4. Configure authentication
sudo sed -i 's/^local   all             all                                     peer$/local   all             all                                     md5/' /var/lib/pgsql/data/pg_hba.conf

# 5. Reload & test
sudo systemctl reload postgresql
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "SELECT version();"

# 6. Import schema
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost < database/schema.sql
```

---

## 🎨 DBeaver GUI Setup

### Connection Details:
```
Host:     localhost
Port:     5432
Database: dastern
Username: dastern
Password: dastern_secure_password_2026
```

### Steps:
1. Database → New Database Connection
2. Select PostgreSQL
3. Enter above details
4. Test Connection
5. Right-click database → SQL Editor → Open SQL Script
6. Select `database/schema.sql`
7. Press Ctrl+Enter

---

## ✅ Verify Setup Works

```bash
# Test connection
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "SELECT version();"

# List all tables (should show many)
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "\dt"

# Count tables
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
```

---

## 🆘 Common Issues & Fixes

| Error | Fix |
|-------|-----|
| `Access denied` | Change `peer` to `md5` in pg_hba.conf, then reload |
| `Port 5432 in use` | Use different port or kill process |
| `Database doesn't exist` | Run: `sudo -u postgres createdb -O dastern dastern` |
| `Connection refused` | Check: `sudo systemctl status postgresql` |
| `pg_hba.conf missing` | Run: `sudo postgresql-setup initdb` |

---

## 📝 Connection String (for app config)

```
postgresql://dastern:dastern_secure_password_2026@localhost:5432/dastern
```

Save to `.env`:
```bash
DATABASE_URL=postgresql://dastern:dastern_secure_password_2026@localhost:5432/dastern
```

---

## 🐳 Docker Commands

```bash
# Start database
docker-compose up -d postgres

# Stop database
docker-compose stop postgres

# View logs
docker-compose logs -f postgres

# Connect to container shell
docker-compose exec postgres bash

# Access psql inside container
docker-compose exec postgres psql -U dastern -d dastern

# Remove database (WARNING: deletes data)
docker-compose down -v postgres
```

---

## 📊 Managing PostgreSQL Service

```bash
# Check status
sudo systemctl status postgresql

# Start/Stop/Restart
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql

# View logs
sudo journalctl -u postgresql -n 50

# Enable on boot
sudo systemctl enable postgresql
```

---

**For detailed guide:** See `DATABASE_SETUP.md`
