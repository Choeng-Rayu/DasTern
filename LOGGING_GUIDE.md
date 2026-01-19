# 🔍 Docker Logging & Debugging Guide - DasTern

Complete guide to check, analyze, and debug logs from all services.

---

## 🎯 Quick Log Commands

### View All Logs (Real-time)
```bash
cd /home/rayu/DasTern
sudo docker compose logs -f
```
Press `Ctrl+C` to stop (services keep running)

### View Specific Service Logs
```bash
sudo docker compose logs -f backend        # Next.js backend
sudo docker compose logs -f ocr-service    # OCR service
sudo docker compose logs -f ai-llm-service # AI service
```

---

## 📋 Detailed Logging Options

### 1️⃣ View Last N Lines
```bash
# Last 50 lines (default is all)
sudo docker compose logs --tail=50

# Last 100 lines
sudo docker compose logs --tail=100

# Last 20 lines for specific service
sudo docker compose logs --tail=20 backend
```

### 2️⃣ View Logs Since Time
```bash
# Last 5 minutes
sudo docker compose logs --since=5m

# Last 1 hour
sudo docker compose logs --since=1h

# Last 30 seconds
sudo docker compose logs --since=30s

# Since specific time (2025-01-19 10:30:00)
sudo docker compose logs --since=2025-01-19T10:30:00
```

### 3️⃣ View Logs Until Time
```bash
# Logs up to 5 minutes ago
sudo docker compose logs --until=5m

# Logs up to 1 hour ago
sudo docker compose logs --until=1h
```

### 4️⃣ Follow Mode (Live Logs)
```bash
# Follow all services (live)
sudo docker compose logs -f

# Follow specific service with 20 lines history
sudo docker compose logs -f --tail=20 backend

# Follow multiple services
sudo docker compose logs -f backend ocr-service
```

### 5️⃣ Timestamps
```bash
# Show timestamps
sudo docker compose logs --timestamps

# Show timestamps in UTC
sudo docker compose logs -t

# Follow with timestamps
sudo docker compose logs -ft backend
```

---

## 🔧 Real-World Debugging Scenarios

### Scenario 1: Service Won't Start
```bash
# Check what went wrong
sudo docker compose logs --tail=100 backend

# Common issues:
# - "Module not found" → Missing npm dependencies
# - "EADDRINUSE" → Port already in use
# - "Cannot find module" → Missing files
```

### Scenario 2: Service Crashes After Starting
```bash
# View crash logs
sudo docker compose logs --tail=50 ocr-service

# Look for:
# - ImportError (Python)
# - TypeError
# - RuntimeError
# - Connection errors
```

### Scenario 3: Slow Performance
```bash
# Monitor in real-time
sudo docker compose logs -f backend

# Look for:
# - "WARNING" messages
# - Long response times
# - Memory errors
```

### Scenario 4: API Connection Issues
```bash
# Check if services can communicate
sudo docker compose logs -f

# Backend trying to reach OCR:
# Should see: "POST http://ocr-service:8000"

# If fails, check logs:
sudo docker compose logs backend
# Look for: "Connection refused" or "Name resolution failed"
```

---

## 💾 Save Logs to File

### Save All Logs
```bash
sudo docker compose logs > all_logs.txt
```

### Save Specific Service Logs
```bash
sudo docker compose logs backend > backend.log
sudo docker compose logs ocr-service > ocr.log
sudo docker compose logs ai-llm-service > ai.log
```

### Save Logs with Timestamp
```bash
sudo docker compose logs -t > logs_$(date +%Y%m%d_%H%M%S).txt
```

### View Saved Logs
```bash
# View entire log file
cat backend.log

# View last 100 lines
tail -100 backend.log

# View with line numbers
cat -n backend.log

# Search for specific error
grep "ERROR" backend.log

# Search case-insensitive
grep -i "error" backend.log

# Count occurrences
grep -c "error" backend.log
```

---

## 🔍 Filtering & Searching Logs

### Filter by Service
```bash
# Only show backend logs
sudo docker compose logs backend

# Only show errors
sudo docker compose logs | grep -i error

# Only show warnings
sudo docker compose logs | grep -i warning
```

### Search for Specific Text
```bash
# Find all "connection" related logs
sudo docker compose logs | grep -i connection

# Find specific error code
sudo docker compose logs | grep "404\|500\|error"

# Find API requests
sudo docker compose logs backend | grep "POST\|GET\|PUT"
```

### Time-Based Filtering
```bash
# Logs from last 10 minutes
sudo docker compose logs --since=10m --until=5m

# Save logs from last hour to file
sudo docker compose logs --since=1h > recent_logs.txt
```

---

## 📊 Log Interpretation Guide

### 🔴 ERROR Logs (Critical Issues)
```
ERROR: Connection refused to ocr-service:8000
→ OCR service not running or port not exposed

ERROR: FileNotFoundError: /app/models/model.safetensors
→ Required file missing (download models!)

ERROR: ModuleNotFoundError: No module named 'cv2'
→ Python dependency missing (rebuild Docker)
```

### 🟡 WARNING Logs (Should Watch)
```
WARNING: Slow API response (5000ms)
→ Service is slow, may timeout

WARNING: Using deprecated API endpoint
→ Update code to use new API

WARNING: High memory usage
→ May crash if continues
```

### 🟢 INFO Logs (Normal Operation)
```
INFO: Server started on port 3000
→ Service running successfully

INFO: Processing image from user_123
→ Normal operation

INFO: Database connected
→ Connection successful
```

---

## 🐛 Common Issues & Log Examples

### Issue 1: Backend Can't Connect to OCR Service

**Logs show:**
```
ERROR: Failed to connect to http://ocr-service:8000
Connection refused
```

**Solution:**
```bash
# Check if OCR container is running
sudo docker compose ps

# Check OCR logs
sudo docker compose logs ocr-service

# Restart OCR
sudo docker compose restart ocr-service
```

### Issue 2: Python Module Not Found

**Logs show:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solution:**
```bash
# Check requirements.txt
cat ai-llm-service/requirements.txt

# Rebuild container
sudo docker compose down
sudo docker compose up -d --build ai-llm-service
```

### Issue 3: Port Already in Use

**Logs show:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: 
bind: address already in use
```

**Solution:**
```bash
# Find what's using port 3000
sudo ss -tulpn | grep :3000

# Kill it
sudo kill -9 <PID>

# Restart Docker
sudo docker compose restart backend
```

### Issue 4: Out of Memory

**Logs show:**
```
Killed (exit code: 137)
Cannot allocate memory
```

**Solution:**
```bash
# Check resource usage
sudo docker stats

# Increase memory limit in docker-compose.yml
# or restart with clean state
sudo docker compose down
sudo docker system prune -a
sudo docker compose up -d
```

---

## 📈 Real-Time Monitoring

### Monitor All Services (Interactive)
```bash
# Watch resource usage
sudo docker stats

# Press Ctrl+C to stop
```

### Watch Specific Service
```bash
sudo docker stats dastern-backend
sudo docker stats dastern-ocr
sudo docker stats dastern-ai
```

### Monitor and Log Simultaneously
```bash
# Terminal 1: Watch stats
sudo docker stats

# Terminal 2: Watch logs
sudo docker compose logs -f
```

---

## 🎬 Advanced Log Scenarios

### Scenario: Track Request Through All Services

**1. Request comes to Backend**
```bash
sudo docker compose logs backend | grep "POST /api/ocr"
# Shows: Received request from user
```

**2. Backend calls OCR Service**
```bash
sudo docker compose logs ocr-service | grep "processing"
# Shows: Processing image
```

**3. OCR returns result to Backend**
```bash
sudo docker compose logs backend | grep "ocr response"
# Shows: Received OCR result
```

**4. Backend calls AI Service**
```bash
sudo docker compose logs ai-llm-service | grep "correction"
# Shows: Correcting text
```

**Example Command:**
```bash
# See full flow
sudo docker compose logs --since=5m | grep -E "POST|response|error"
```

### Scenario: Debug Slow API

```bash
# Watch backend performance
sudo docker compose logs -f backend | grep -E "started|completed|duration"

# Check OCR speed
sudo docker compose logs -f ocr-service | grep -E "processing|duration"

# Check AI speed
sudo docker compose logs -f ai-llm-service | grep -E "correcting|duration"
```

---

## 💾 Log Rotation & Cleanup

### View Log Size
```bash
sudo docker system df

# Shows disk usage of images, containers, volumes
```

### Clean Old Logs
```bash
# Remove all stopped containers
sudo docker container prune -f

# Remove unused images
sudo docker image prune -f

# Full cleanup
sudo docker system prune -af
```

---

## 📝 Useful Log Analysis Commands

### Count Errors
```bash
sudo docker compose logs | grep -ic error
```

### Show Only Last Error
```bash
sudo docker compose logs | grep -i error | tail -1
```

### Find All Unique Errors
```bash
sudo docker compose logs | grep -i error | sort -u
```

### Timeline of Events
```bash
sudo docker compose logs -t | sort
```

### Find Errors in Specific Time Range
```bash
sudo docker compose logs --since=10m --until=5m | grep -i error
```

---

## 🎓 Quick Reference Card

| Command | Purpose |
|---------|---------|
| `sudo docker compose logs -f` | Follow all logs (live) |
| `sudo docker compose logs -f backend` | Follow backend only |
| `sudo docker compose logs --tail=50 ocr-service` | Last 50 lines of OCR |
| `sudo docker compose logs --since=10m` | Last 10 minutes |
| `sudo docker compose logs > logs.txt` | Save all logs |
| `sudo docker compose logs \| grep error` | Search for errors |
| `sudo docker stats` | View resource usage |
| `sudo docker compose ps` | Check if running |
| `sudo docker logs <container_id>` | View specific container |

---

## 🚀 Complete Debugging Workflow

### Step 1: Something is broken
```bash
# Check if services are running
sudo docker compose ps
```

### Step 2: View the error
```bash
# Check all logs for errors
sudo docker compose logs | grep -i error
```

### Step 3: Isolate the problem
```bash
# Check specific service
sudo docker compose logs <service-name> | grep -i error
```

### Step 4: Get more context
```bash
# View 100 lines around the error
sudo docker compose logs --tail=100 <service-name>
```

### Step 5: Fix and verify
```bash
# After fixing, restart service
sudo docker compose restart <service-name>

# Watch logs for success
sudo docker compose logs -f <service-name>
```

---

## 📞 Still Stuck?

1. **Save logs to file:**
   ```bash
   sudo docker compose logs > debug_logs.txt
   ```

2. **Check resource usage:**
   ```bash
   sudo docker stats
   ```

3. **Restart everything:**
   ```bash
   sudo docker compose restart
   ```

4. **Nuclear option:**
   ```bash
   sudo docker compose down
   sudo docker system prune -af
   sudo docker compose up -d --build
   ```

5. **Share with team:**
   ```bash
   # Send debug_logs.txt to team for analysis
   ```

---

**Tip:** Always check logs first when debugging! Most issues are visible in the logs. 🔍
