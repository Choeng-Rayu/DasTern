# 🐳 Docker Management Guide - DasTern

Quick reference for running, stopping, and debugging Docker containers.

---

## 🚀 Starting Services

### Start All Services (Detached Mode - Recommended)
```bash
cd /home/rayu/DasTern
sudo docker compose up -d
```
✅ Services run in background, terminal is free to use

### Start All Services (With Logs)
```bash
sudo docker compose up
```
❌ Terminal shows live logs, press Ctrl+C to stop

### Rebuild and Start (After Code Changes)
```bash
sudo docker compose up -d --build
```

---

## 🛑 Stopping Services

### Stop All Services (Keep Containers)
```bash
sudo docker compose stop
```
✅ Fast restart with `sudo docker compose start`

### Stop and Remove All Containers
```bash
sudo docker compose down
```
✅ Clean shutdown, removes containers but keeps images

### Stop and Remove Everything (Nuclear Option)
```bash
sudo docker compose down -v
```
⚠️ Removes containers, networks, AND volumes (data loss!)

---

## 🔍 Checking Status

### View Running Containers
```bash
sudo docker compose ps
```

### View All Containers (Including Stopped)
```bash
sudo docker ps -a
```

### Check Service Health
```bash
# Check if services are responding
curl http://localhost:3000/api/health  # Backend
curl http://localhost:8000/health      # OCR Service
curl http://localhost:8001/health      # AI Service
```

---

## 📋 Viewing Logs

### View All Logs (Live)
```bash
sudo docker compose logs -f
```
Press Ctrl+C to stop viewing (services keep running)

### View Logs for Specific Service
```bash
sudo docker compose logs -f backend        # Next.js backend
sudo docker compose logs -f ocr-service    # OCR service
sudo docker compose logs -f ai-llm-service # AI service
```

### View Last 100 Lines
```bash
sudo docker compose logs --tail=100
```

### View Logs Since Time
```bash
sudo docker compose logs --since 10m  # Last 10 minutes
sudo docker compose logs --since 1h   # Last hour
```

---

## 🔄 Restarting Services

### Restart All Services
```bash
sudo docker compose restart
```

### Restart Single Service
```bash
sudo docker compose restart backend
sudo docker compose restart ocr-service
sudo docker compose restart ai-llm-service
```

---

## 🐛 Debugging Issues

### Issue 1: Port Already in Use

**Error:** `bind: address already in use`

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :3000
sudo ss -tlnp | grep :3000

# Kill the process
sudo kill -9 <PID>

# Restart Docker
sudo docker compose up -d
```

### Issue 2: Container Won't Start

**Check logs:**
```bash
sudo docker compose logs <service-name>
```

**Common causes:**
- Missing `.env` file → `cp .env.example .env`
- Wrong file permissions
- Syntax error in Dockerfile
- Missing dependencies in requirements.txt or package.json

### Issue 3: Container Keeps Restarting

```bash
# Check container status
sudo docker compose ps

# View crash logs
sudo docker compose logs --tail=50 <service-name>
```

### Issue 4: Cannot Connect to Service

```bash
# Check if container is running
sudo docker compose ps

# Check if port is exposed
sudo docker port dastern-backend

# Check network
sudo docker network ls
sudo docker network inspect dastern_dastern-network
```

### Issue 5: Changes Not Reflected

```bash
# Rebuild without cache
sudo docker compose build --no-cache
sudo docker compose up -d
```

---

## 🔧 Advanced Commands

### Execute Command Inside Container
```bash
# Open bash shell in backend
sudo docker compose exec backend /bin/sh

# Run npm command
sudo docker compose exec backend npm install

# Run Python command in OCR service
sudo docker compose exec ocr-service python -c "import cv2; print(cv2.__version__)"
```

### View Container Resource Usage
```bash
sudo docker stats
```

### Clean Up Unused Resources
```bash
# Remove stopped containers
sudo docker container prune

# Remove unused images
sudo docker image prune

# Remove unused volumes
sudo docker volume prune

# Remove everything unused (CAREFUL!)
sudo docker system prune -af
```

---

## 📊 Quick Health Check

Run this to check all services:
```bash
echo "🔍 Checking DasTern Services..."
echo ""
echo "📦 Containers:"
sudo docker compose ps
echo ""
echo "🌐 Backend (Next.js):"
curl -s http://localhost:3000/api/health || echo "❌ Not responding"
echo ""
echo "🔤 OCR Service:"
curl -s http://localhost:8000/health || echo "❌ Not responding"
echo ""
echo "🤖 AI Service:"
curl -s http://localhost:8001/health || echo "❌ Not responding"
```

---

## 🎓 Common Workflows

### Daily Development Workflow
```bash
# Morning: Start services
cd /home/rayu/DasTern
sudo docker compose up -d

# Check everything is running
sudo docker compose ps

# View logs if needed
sudo docker compose logs -f

# Evening: Stop services
sudo docker compose stop
```

### After Changing Code
```bash
# Backend (Next.js) - Hot reload works automatically
# Just save file, changes appear

# Python services - Need rebuild
sudo docker compose up -d --build ocr-service
sudo docker compose up -d --build ai-llm-service
```

### When Things Break
```bash
# 1. Check logs
sudo docker compose logs -f

# 2. Restart everything
sudo docker compose restart

# 3. If still broken, rebuild
sudo docker compose down
sudo docker compose up -d --build

# 4. Nuclear option
sudo docker compose down -v
sudo docker system prune -af
sudo docker compose up -d --build
```

---

## 🚨 Emergency Commands

### Stop Everything Immediately
```bash
sudo docker stop $(sudo docker ps -q)
```

### Kill All Containers
```bash
sudo docker kill $(sudo docker ps -q)
```

### Remove All Containers
```bash
sudo docker rm -f $(sudo docker ps -aq)
```

---

## ✅ Quick Reference Card

| Task | Command |
|------|---------|
| Start | `sudo docker compose up -d` |
| Stop | `sudo docker compose stop` |
| Restart | `sudo docker compose restart` |
| Logs | `sudo docker compose logs -f` |
| Status | `sudo docker compose ps` |
| Rebuild | `sudo docker compose up -d --build` |
| Clean | `sudo docker compose down` |
| Shell | `sudo docker compose exec <service> /bin/sh` |

---

## 💡 Pro Tips

1. **Always use `-d` flag** for background running
2. **Check logs first** when debugging: `sudo docker compose logs -f`
3. **Rebuild after dependency changes** (package.json, requirements.txt)
4. **Use `--build` flag** when you change Dockerfile or dependencies
5. **Don't use `docker compose down -v`** unless you want to lose data
6. **One service restart** is faster than restarting all

---

## 📞 Still Having Issues?

1. Check logs: `sudo docker compose logs -f`
2. Check [SETUP.md](SETUP.md) for environment setup
3. Verify `.env` file exists and has correct values
4. Ensure ports 3000, 8000, 8001 are not in use
5. Try rebuilding: `sudo docker compose up -d --build`
6. Check Docker daemon is running: `sudo systemctl status docker`

---

**Current Status:** All services running! 🎉
- Backend: http://localhost:3000
- OCR: http://localhost:8000
- AI: http://localhost:8001
