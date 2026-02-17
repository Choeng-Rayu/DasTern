# Docker & Database Management - Quick Reference

## 🎯 Current Setup

### Database Strategy: COPY (Not Volume Mount)

The database schema is **built into the Docker image**, not mounted from the host:

**Advantages:**
- ✅ No file permission issues
- ✅ Works across all systems (Linux, Mac, Windows)
- ✅ Consistent deployments
- ✅ No host filesystem dependencies

**Trade-off:**
- Requires rebuild to update base schema
- Migrations must be applied to running containers

---

## 🚀 Common Tasks

### 1. Initial Setup

```bash
# Build all services
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 2. Apply Database Migration

```bash
# Use the migration script (easiest)
./database/migrate.sh database/migrations/004_new_feature.sql

# Or manually with docker exec
docker exec -i dastern-postgres psql -U dastern -d dastern < database/migrations/004_new_feature.sql
```

### 3. Rebuild Services

```bash
# Rebuild specific service
docker compose build ocr-service

# Rebuild without cache (fresh build)
docker compose build --no-cache ocr-service

# Rebuild all services
docker compose build

# After rebuild, restart
docker compose down
docker compose up -d
```

### 4. Reset Database (DESTRUCTIVE)

⚠️ **This deletes all data!**

```bash
# Stop containers
docker compose down

# Remove database volume
docker volume rm dastern_postgres_data

# Rebuild postgres with updated schema
docker compose build postgres

# Start fresh
docker compose up -d
```

### 5. Backup & Restore

```bash
# Backup
docker exec dastern-postgres pg_dump -U dastern dastern > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i dastern-postgres psql -U dastern -d dastern < backup_20260126.sql
```

---

## 🔧 Troubleshooting

### OCR Service Fails with Import Errors

```bash
# The OCR image was likely cached with old dependencies
# Rebuild without cache:
docker compose build --no-cache ocr-service
docker compose up -d ocr-service

# Check logs
docker compose logs -f ocr-service
```

### Database Schema Outdated

```bash
# Apply new migrations
./database/migrate.sh database/migrations/XXX_update.sql

# Or rebuild (loses data)
docker compose down
docker volume rm dastern_postgres_data
docker compose build postgres
docker compose up -d
```

### Service Won't Start

```bash
# Check logs
docker compose logs [service-name]

# Check status
docker compose ps

# Restart specific service
docker compose restart [service-name]

# Force recreate
docker compose up -d --force-recreate [service-name]
```

### Network Issues During Build

```bash
# If build fails with "network is unreachable"
# Wait a moment and retry:
docker compose build --no-cache [service-name]

# Or pull base images first:
docker pull python:3.10-slim
docker pull python:3.11-slim
docker pull postgres:16-alpine
docker pull node:20-slim
```

---

## 📁 File Structure

```
DasTern/
├── database/
│   ├── Dockerfile           # Custom Postgres image
│   ├── final-schema.sql     # Base schema (built into image)
│   ├── migrate.sh           # Migration helper script
│   └── migrations/
│       ├── 001_initial_schema.sql
│       ├── 002_enhanced_prescriptions.sql
│       └── 003_family_and_reports.sql
├── ocr-service/
│   └── Dockerfile           # Fixed with libgl1
├── ai-llm-service/
│   └── Dockerfile
├── backend-nextjs/
│   └── Dockerfile
├── docker-compose.yml        # Main orchestration
├── .env                      # Environment variables (not committed)
└── .env.example              # Template
```

---

## 🐛 Known Issues & Fixes

### Issue: libGL.so.1 missing in OCR service

**Symptom:**
```
ImportError: libGL.so.1: cannot open shared object file
```

**Fix:**
The Dockerfile now includes `libgl1`:
```dockerfile
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \      # ← Added this
    curl \
    && rm -rf /var/lib/apt/lists/*
```

**Rebuild:**
```bash
docker compose build --no-cache ocr-service
docker compose up -d
```

### Issue: Old cached image being used

**Solution:**
```bash
# Force rebuild without cache
docker compose build --no-cache [service]

# Or remove old image first
docker rmi dastern-ocr-service
docker compose build ocr-service
```

---

## 🔄 Development vs Production

### Production Mode (Current)

Code is **copied into images** during build:
- Clean, isolated containers
- Requires rebuild for code changes
- Better for deployment

### Development Mode (Optional)

Uncomment volume mounts in `docker-compose.yml`:
```yaml
volumes:
  - ./ocr-service:/app  # ← Uncomment for hot reload
```

**Note:** This can cause issues if the container expects different permissions or structure.

---

## 📊 Service Health Checks

All services have health checks:

```bash
# View health status
docker compose ps

# Inspect specific health check
docker inspect dastern-postgres --format='{{.State.Health.Status}}'

# Manual health check
curl http://localhost:3000/  # Backend
curl http://localhost:8001/health  # AI Service
curl http://localhost:8002/  # OCR Service
```

---

## 🎓 Best Practices

1. **Always backup before migrations:**
   ```bash
   docker exec dastern-postgres pg_dump -U dastern dastern > backup.sql
   ```

2. **Test migrations on dev first:**
   ```bash
   # Apply to dev
   ./database/migrate.sh migrations/test.sql
   
   # Test the changes
   # If OK, apply to prod
   ```

3. **Use transactions in migrations:**
   ```sql
   BEGIN;
   -- your changes
   COMMIT;
   ```

4. **Document your changes:**
   - Add comments to SQL files
   - Update schema documentation
   - Track applied migrations

5. **Monitor logs during deployment:**
   ```bash
   docker compose logs -f
   ```

---

## 📞 Quick Commands Cheat Sheet

```bash
# Status
docker compose ps
docker compose logs -f [service]

# Start/Stop
docker compose up -d
docker compose down
docker compose restart [service]

# Build
docker compose build [service]
docker compose build --no-cache [service]

# Database
./database/migrate.sh migrations/XXX.sql
docker exec -it dastern-postgres psql -U dastern -d dastern

# Cleanup
docker compose down -v  # Remove volumes
docker system prune -a  # Remove unused images

# Backup/Restore
docker exec dastern-postgres pg_dump -U dastern dastern > backup.sql
docker exec -i dastern-postgres psql -U dastern -d dastern < backup.sql
```

---

For detailed migration workflows, see: [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md)
