# 🚀 DasTern Docker - Quick Start Guide

## Current Status ✅

Your Docker setup is now ready! Here's what's running:

### ✅ **PostgreSQL Database**
- **Status**: Running and Healthy ✓
- **Container**: dastern-postgres
- **Port**: 5432
- **Database**: dastern
- **User**: dastern
- **Tables**: 20 tables imported successfully

### 🔄 **Services Building**
- OCR Service (estimating 10-15 minutes)
- AI/LLM Service (estimating 10-15 minutes)
- Next.js Backend

---

## 🎯 What to Do Now

### Option 1: Wait for All Services (Recommended)
```bash
cd ~/DasTern

# Watch the build progress
docker compose logs -f

# Or in another terminal, check status
docker compose ps
```

**Expected Output After Build:**
```
NAME                     IMAGE              STATUS
dastern-postgres         postgres:16       Up (healthy)
dastern-backend          dastern-backend   Up
dastern-ocr              dastern-ocr       Up
dastern-ai               dastern-ai        Up
```

### Option 2: Access Services As They Come Online

#### PostgreSQL (Ready Now)
```bash
# Connect to the database
docker compose exec postgres psql -U dastern -d dastern

# List all tables
\dt

# Exit
\q
```

#### Backend (Coming Soon)
Once ready, access at: **http://localhost:3000**

#### OCR Service (Coming Soon)
Once ready, access at: **http://localhost:8000**

#### AI Service (Coming Soon)
Once ready, access at: **http://localhost:8001**

---

## 📋 Useful Commands

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f postgres
docker compose logs -f backend
docker compose logs -f ocr-service
docker compose logs -f ai-llm-service
```

### Stop Services
```bash
# Stop all
docker compose stop

# Stop specific
docker compose stop backend
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific
docker compose restart backend
```

### Remove Everything (Clean slate)
```bash
docker compose down -v
```

### Connect to Database from Host

If you want to connect from DBeaver or CLI outside Docker:

```bash
# Using psql
PGPASSWORD='dastern_secure_password_2026' psql -U dastern -d dastern -h localhost -p 5432

# Using DBeaver:
# Host: localhost
# Port: 5432
# Database: dastern
# Username: dastern
# Password: dastern_secure_password_2026
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose logs service-name

# Rebuild without cache
docker compose build --no-cache service-name

# Remove and restart
docker compose down
docker compose up -d
```

### Port Already in Use
```bash
# Check what's using the port
sudo ss -tlnp | grep 3000

# Kill the process or change port in docker-compose.yml
```

### Database Connection Issues
```bash
# Test database directly
docker compose exec postgres psql -U dastern -d dastern -c "SELECT 1;"

# Reset database (WARNING: deletes data)
docker compose down -v postgres
docker compose up -d postgres
```

### Out of Disk Space
```bash
# Clean up Docker
docker system prune -a

# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune
```

---

## 📊 Environment Variables

Your `.env` file is configured with:

```bash
# Database
DB_USER=dastern
DB_PASSWORD=dastern_secure_password_2026
DB_NAME=dastern
DB_PORT=5432
DATABASE_URL=postgresql://dastern:dastern_secure_password_2026@postgres:5432/dastern

# Services
OCR_SERVICE_URL=http://ocr-service:8000
AI_SERVICE_URL=http://ai-llm-service:8001

# App
NODE_ENV=development
NEXTAUTH_URL=http://localhost:3000
```

---

## 🔍 Verify Everything Works

### Test Database
```bash
docker compose exec postgres psql -U dastern -d dastern << EOF
SELECT 
  (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public') as "Table Count",
  version() as "PostgreSQL Version";
EOF
```

### Test Backend (once running)
```bash
curl http://localhost:3000
```

### Test OCR Service (once running)
```bash
curl http://localhost:8000/docs
```

### Test AI Service (once running)
```bash
curl http://localhost:8001/docs
```

---

## 📁 Project Structure

```
DasTern/
├── database/              # PostgreSQL schema & migrations
│   ├── schema.sql        # ✅ Imported to database
│   ├── migrations/
│   └── seeds/
├── backend-nextjs/       # Next.js application
├── ocr-service/          # OCR with Tesseract & MT5
├── ai-llm-service/       # AI with MT5 model
├── docker-compose.yml    # ✅ All services defined
└── .env                  # ✅ Configuration ready
```

---

## ⏱️ Build Times (Approximate)

| Service | Time | Status |
|---------|------|--------|
| PostgreSQL | 1 min | ✅ Done |
| Backend (Next.js) | 3-5 min | 🔄 Building |
| OCR Service | 10-15 min | 🔄 Building |
| AI Service | 10-15 min | 🔄 Building |

**Total**: ~25-35 minutes for first build (subsequent builds are faster due to caching)

---

## 🎓 Next Steps

1. **Wait for build to complete** - Watch `docker compose logs -f`
2. **Test the database** - Already done! ✅
3. **Access the backend** - http://localhost:3000 (once ready)
4. **Set up DBeaver** - Connect to localhost:5432
5. **Read documentation**:
   - [DATABASE_SETUP.md](DATABASE_SETUP.md) - Complete database guide
   - [DATABASE_QUICK_SETUP.md](DATABASE_QUICK_SETUP.md) - Quick reference
   - [README.md](README.md) - Project overview

---

## 📞 Need Help?

```bash
# View all service logs in real-time
docker compose logs -f

# Check specific error
docker compose logs backend | grep -i error

# Rebuild a service
docker compose build --no-cache ocr-service

# Get shell access to a container
docker compose exec backend bash
```

---

**Everything is set up and running! 🎉 Your database is ready, and services will be online shortly.**
