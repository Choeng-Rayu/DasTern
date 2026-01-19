# 🔍 Docker Logging Quick Card

**Print this page and keep it handy!**

---

## ⚡ Most Used Commands

```bash
# Check status
sudo docker compose ps

# View all logs (live)
sudo docker compose logs -f

# View backend logs
sudo docker compose logs -f backend

# View OCR logs
sudo docker compose logs -f ocr-service

# View AI logs
sudo docker compose logs -f ai-llm-service

# Last 50 lines
sudo docker compose logs --tail=50

# Search for errors
sudo docker compose logs | grep -i error

# Save to file
sudo docker compose logs > logs.txt

# View saved logs
cat logs.txt

# Monitor resources
sudo docker stats
```

---

## 🎯 When Something Breaks

| Problem | Command | Look For |
|---------|---------|----------|
| Service won't start | `sudo docker compose logs <service>` | ERROR, ImportError, Connection refused |
| Slow response | `sudo docker compose logs backend` | Response time in ms |
| Can't reach service | `sudo docker compose logs backend` | Connection refused, Name resolution failed |
| Memory issues | `sudo docker stats` | Memory % > 80% |
| Port conflict | `sudo ss -tulpn \| grep :3000` | LISTEN state |

---

## 📋 One-Liners

```bash
# Find all errors
sudo docker compose logs | grep -i error

# Find warnings
sudo docker compose logs | grep -i warning

# Count errors
sudo docker compose logs | grep -ic error

# View errors with context (3 lines before/after)
sudo docker compose logs | grep -i -B3 -A3 error

# View last 2 hours
sudo docker compose logs --since=2h

# View since specific time
sudo docker compose logs --since=2026-01-19T10:30:00
```

---

## 🔧 Debugging Checklist

- [ ] `sudo docker compose ps` - Check if services running
- [ ] `sudo docker compose logs -f` - Watch live logs
- [ ] `sudo docker compose logs <service>` - Check specific service
- [ ] `sudo docker compose logs | grep error` - Find errors
- [ ] `sudo docker stats` - Check resources
- [ ] `sudo docker compose restart <service>` - Restart if needed
- [ ] `sudo docker compose down && sudo docker compose up -d` - Full restart

---

**Keep this handy when debugging! 90% of issues are visible in logs.** 🎯
