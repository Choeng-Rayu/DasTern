# 🎯 DasTern - Quick Reference Card

## 🚀 One Command Setup

```bash
docker compose up --build
```

---

## 🌿 Git Workflow Cheat Sheet

### Start New Feature
```bash
git checkout develop && git pull origin develop
git checkout -b feature/my-task
```

### Before PR
```bash
git fetch origin && git merge develop
docker compose up  # TEST!
git push origin feature/my-task
```

### Branch Rules
- ✅ `feature/ocr-preprocess`
- ✅ `fix/docker-build`
- ❌ Never push to `main`
- ❌ Never push to `develop`

---

## 🐳 Docker Commands

| Command | Purpose |
|---------|---------|
| `docker compose up` | Start all services |
| `docker compose up -d` | Start in background |
| `docker compose down` | Stop all services |
| `docker compose logs -f` | View all logs |
| `docker compose restart backend` | Restart one service |
| `docker compose up --build` | Rebuild and start |

---

## 🔗 Service URLs

- Backend: http://localhost:3000
- OCR: http://localhost:8000
- AI LLM: http://localhost:8001

---

## 📁 Folder = Service

```
backend-nextjs/    → Next.js API Gateway
ocr-service/       → Python OCR
ai-llm-service/    → Python AI/LLM
mobile-flutter/    → Flutter App
```

---

## ⚠️ Before First Run

1. `cp .env.example .env` (edit values)
2. Download MT5 models (see [SETUP.md](SETUP.md))
3. `docker compose up --build`

---

## 🛡️ GitHub Branch Protection

**Repo Admin:** Set up protection on `main` branch
- Settings → Branches → Add rule
- Pattern: `main`
- ✅ Require PR reviews
- ✅ Block force push

---

## 💬 Defense Talking Points

**Q: Why separate services?**
> "Single-responsibility principle. OCR handles visual extraction, AI handles language understanding. This improves scalability and maintainability."

**Q: Why Docker?**
> "Eliminates environment inconsistencies. Every developer runs identical configurations, preventing 'works on my machine' issues."

**Q: Why branch protection?**
> "Enforces code review, prevents accidental main branch corruption, and maintains stable demo/defense version."

---

## 📞 Need Help?

1. Check [SETUP.md](SETUP.md)
2. Check [README.md](README.md)
3. Ask team
4. Check Docker logs: `docker compose logs -f`
