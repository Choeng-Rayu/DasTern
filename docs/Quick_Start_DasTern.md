# 🚀 DasTern Quick Start Guide - Docker & Development Workflow

Complete step-by-step guide for running Docker with all services, modifying code, and viewing live logs.

---

## 📋 Table of Contents

1. [Starting Docker with All Services](#starting-docker-with-all-services)
2. [Modifying Code During Development](#modifying-code-during-development)
3. [Viewing Live Logs](#viewing-live-logs)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Starting Docker with All Services

### **Option 1: Automated Script (Easiest - Recommended)**

```bash
cd ~/DasTern
./docker-start.sh
```

**What it does:**
- ✅ Stops any old containers
- ✅ Cleans up Docker system
- ✅ Starts PostgreSQL database
- ✅ Builds Backend (Next.js)
- ✅ Builds OCR Service (Python + Tesseract)
- ✅ Builds AI Service (Python + PyTorch)
- ✅ Starts all services
- ✅ Shows connection details

**Expected Output:**
```
✅ PostgreSQL is ready!
✅ Database has 20 tables imported ✓
Building Backend...
Building OCR Service...
Building AI Service...
Starting All Services...

🎉 DasTern is Ready!
Services available at:
- Backend: http://localhost:3000
- OCR: http://localhost:8000
- AI: http://localhost:8001
```

**Total Time:** 25-35 minutes (first run), 2-5 minutes (subsequent runs)

---

### **Option 2: Manual Commands**

```bash
cd ~/DasTern

# Start all services
docker compose up -d

# OR start specific services
docker compose up -d postgres          # Database only
docker compose up -d backend           # Next.js only
docker compose up -d ocr-service       # OCR only
docker compose up -d ai-llm-service    # AI only
```

---

### **Option 3: View Build Progress While Building**

```bash
cd ~/DasTern

# Start services in foreground (see all build logs)
docker compose up

# In another terminal, press Ctrl+C to stop the foreground view when done building
```

---

## 💻 Modifying Code During Development

### **🔄 Backend (Next.js) - Hot Reload**

The backend automatically reloads when you modify code!

**Steps:**
1. Open file in VS Code: `backend-nextjs/app/page.tsx` or any other file
2. Make changes (e.g., edit text content)
3. Save the file (Ctrl+S)
4. **Automatic reload** - No restart needed!
5. View changes at: http://localhost:3000

**Example:**
```typescript
// backend-nextjs/app/page.tsx
export default function Home() {
  return (
    <div>
      <h1>My DasTern App</h1>  {/* Edit this text */}
    </div>
  )
}
```

Save → Changes appear automatically at http://localhost:3000 ✅

---

### **🐍 OCR Service - Manual Restart Required**

Code changes need a restart.

**Steps:**
1. Edit file: `ocr-service/app/main.py` or other Python files
2. Save the file
3. Restart the service:
```bash
cd ~/DasTern
docker compose restart ocr-service
```
4. View logs to verify:
```bash
docker compose logs -f ocr-service
```

---

### **🤖 AI Service - Manual Restart Required**

Code changes need a restart.

**Steps:**
1. Edit file: `ai-llm-service/app/main.py` or other Python files
2. Save the file
3. Restart the service:
```bash
cd ~/DasTern
docker compose restart ai-llm-service
```
4. View logs to verify:
```bash
docker compose logs -f ai-llm-service
```

---

### **🗄️ Database Schema Changes**

If you modify `database/schema.sql`:

```bash
cd ~/DasTern

# Reset database and reimport schema
docker compose down -v postgres     # Remove database
docker compose up -d postgres       # Recreate with new schema
```

---

## 📊 Viewing Live Logs

### **View All Services Logs (Live Stream)**

```bash
cd ~/DasTern

# Watch all services in real-time
docker compose logs -f

# Press Ctrl+C to stop watching
```

**Output shows:**
```
dastern-postgres     | LOG: database system is ready
dastern-backend      | ready - started server on 0.0.0.0:3000
dastern-ocr          | INFO: Started server process
dastern-ai           | INFO: Started server process
```

---

### **View Specific Service Logs (Live Stream)**

#### **PostgreSQL Logs**
```bash
docker compose logs -f postgres

# Shows database connections, queries, errors
# Example output:
# dastern-postgres | LOG: checkpoint complete
# dastern-postgres | LOG: connection from user "dastern"
```

#### **Backend (Next.js) Logs**
```bash
docker compose logs -f backend

# Shows HTTP requests, errors, build info
# Example output:
# dastern-backend | GET / 200 45ms
# dastern-backend | Compiled /app/app/page.tsx
# dastern-backend | GET /api/data 500 12ms - Error in endpoint
```

#### **OCR Service Logs**
```bash
docker compose logs -f ocr-service

# Shows OCR processing, Tesseract info, Python errors
# Example output:
# dastern-ocr | INFO: GET /process 200
# dastern-ocr | Processing image with Tesseract...
# dastern-ocr | OCR confidence: 0.95
```

#### **AI Service Logs**
```bash
docker compose logs -f ai-llm-service

# Shows ML model loading, predictions, errors
# Example output:
# dastern-ai | INFO: Loading MT5 model...
# dastern-ai | Model loaded successfully
# dastern-ai | Generating text prediction...
```

---

### **View Last N Lines of Logs**

```bash
# View last 50 lines without following
docker compose logs --tail=50 backend

# View last 100 lines of all services
docker compose logs --tail=100
```

---

### **View Logs with Timestamps**

```bash
# Show timestamps for each log line
docker compose logs -f --timestamps backend

# Example output:
# 2026-01-21T10:30:45.123Z dastern-backend | GET / 200
# 2026-01-21T10:30:46.456Z dastern-backend | GET /api/data 500
```

---

### **Filter Logs by Keywords**

```bash
# View only error logs
docker compose logs backend | grep -i error

# View only WARNING logs
docker compose logs ocr-service | grep -i warning

# View logs containing "Tesseract"
docker compose logs -f | grep Tesseract
```

---

## 🔄 Common Workflows

### **Workflow 1: Daily Development Start**

```bash
# Step 1: Navigate to project
cd ~/DasTern

# Step 2: Check if containers are still running
docker compose ps

# Step 3a: If NOT running, start them
docker compose up -d

# Step 3b: If running, just work on code (no restart needed for backend)

# Step 4: View logs in real-time (in separate terminal)
docker compose logs -f backend

# Step 5: Open browser and test
# Backend: http://localhost:3000
# OCR: http://localhost:8000/docs
# AI: http://localhost:8001/docs
```

---

### **Workflow 2: Modify Backend & Test**

```bash
# Terminal 1: Watch backend logs
cd ~/DasTern
docker compose logs -f backend

# Terminal 2 (or VS Code): Edit code
# Edit: backend-nextjs/app/page.tsx
# Save file (Ctrl+S)
# Changes auto-reload (watch Terminal 1 for "Compiled")
# Refresh browser: http://localhost:3000

# Done! Changes are live
```

---

### **Workflow 3: Modify OCR Service & Test**

```bash
# Terminal 1: Watch OCR logs
cd ~/DasTern
docker compose logs -f ocr-service

# Terminal 2 (or VS Code): Edit code
# Edit: ocr-service/app/main.py
# Save file

# Terminal 1: Restart service
docker compose restart ocr-service

# Watch logs in Terminal 1 for "started server"
# Test endpoint: http://localhost:8000/docs
```

---

### **Workflow 4: Multiple Services Monitoring**

```bash
# Terminal 1: Backend logs
docker compose logs -f backend

# Terminal 2: OCR logs
docker compose logs -f ocr-service

# Terminal 3: AI logs
docker compose logs -f ai-llm-service

# Terminal 4: Database logs
docker compose logs -f postgres

# Terminal 5: Test your app
# Make requests and watch all terminals for activity
```

---

### **Workflow 5: Debug an Endpoint Error**

```bash
# Step 1: See error in logs
cd ~/DasTern
docker compose logs -f backend | grep -i error

# Example error:
# GET /api/users 500 Error: database connection failed

# Step 2: Check which service is affected
docker compose logs -f postgres    # Check database logs

# Step 3: Identify the issue
# - Database not running?
# - Wrong connection string?
# - Missing table?

# Step 4: Fix the code/config

# Step 5: Restart the affected service
docker compose restart backend

# Step 6: Watch logs while it restarts
docker compose logs -f backend
```

---

## 🛑 Stopping & Restarting Services

### **Stop All Services (Keep Data)**

```bash
docker compose stop

# Services stop gracefully but volumes (data) are kept
# Use this when you want to pause development
```

---

### **Restart All Services**

```bash
docker compose restart

# OR restart specific service
docker compose restart backend
docker compose restart ocr-service
```

---

### **Restart & Watch Logs**

```bash
# Restart backend and immediately watch its logs
docker compose restart backend && docker compose logs -f backend

# Useful to see startup messages
```

---

### **Stop Everything (Delete Data)**

```bash
docker compose down -v

# WARNING: This deletes the database!
# Use only if you want fresh start
```

---

## 🐛 Troubleshooting

### **Service Won't Start - Check Logs**

```bash
# View logs of failing service
docker compose logs backend

# Look for error messages like:
# - "port 3000 already in use"
# - "database connection refused"
# - "file not found"
```

---

### **Port Already in Use**

```bash
# Find what's using the port
sudo ss -tlnp | grep 3000

# Solution 1: Kill the process
sudo kill -9 <PID>

# Solution 2: Change port in docker-compose.yml
# Change: "3000:3000" to "3001:3000"
# Then: http://localhost:3001
```

---

### **Database Connection Failed**

```bash
# Check if PostgreSQL is running
docker compose ps postgres

# If not running, start it
docker compose up -d postgres

# Wait 5 seconds for startup
sleep 5

# Verify connection
docker compose exec postgres psql -U dastern -d dastern -c "SELECT 1;"

# Should return:
# ?column?
# --------
#        1
```

---

### **Service Keeps Crashing**

```bash
# View detailed logs
docker compose logs backend

# Look for:
# - Exit codes: 1 (error), 127 (command not found), 139 (crash)
# - Last message before exit

# Rebuild service from scratch
docker compose build --no-cache backend
docker compose up -d backend

# Watch startup logs
docker compose logs -f backend
```

---

### **Out of Disk Space**

```bash
# Clean up Docker
docker system prune -a

# Check disk usage
docker system df

# Remove specific image
docker rmi image-name
```

---

## 📞 Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `./docker-start.sh` | Start all services (recommended) |
| `docker compose up -d` | Start all services |
| `docker compose ps` | Check status |
| `docker compose logs -f` | View all logs live |
| `docker compose logs -f backend` | View backend logs live |
| `docker compose restart backend` | Restart a service |
| `docker compose stop` | Stop all services |
| `docker compose down -v` | Stop and delete data |
| `docker compose exec postgres psql -U dastern -d dastern` | Connect to database |

---

## 🎯 Next Steps

1. **Start services:** `./docker-start.sh` or `docker compose up -d`
2. **Watch logs:** `docker compose logs -f`
3. **Modify code:** Edit files in your editor
4. **See changes:** Auto-reload for backend, manual restart for services
5. **Debug issues:** Check logs with `docker compose logs -f service-name`

---

## 📚 Full Guides

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Database setup details
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker overview
- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker reference

---

**You're all set! Happy coding! 🎉**
