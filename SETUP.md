# 🚀 DasTern Setup Guide

Complete setup guide for new team members.

## 📋 Prerequisites

- Docker & Docker Compose
- Git
- GitHub account with access to the repo

---

## 🔧 First Time Setup

### 1. Clone Repository

```bash
git clone https://github.com/Choeng-Rayu/DasTern.git
cd DasTern
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dastern
JWT_SECRET=your-secret-key-here
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

### 3. Download AI Models

The MT5 model files are too large for Git. Download them:

```bash
cd ai-llm-service/models/
pip install transformers torch
python -c "
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
model = MT5ForConditionalGeneration.from_pretrained('google/mt5-small')
tokenizer = MT5Tokenizer.from_pretrained('google/mt5-small')
model.save_pretrained('./mt5-small/model')
tokenizer.save_pretrained('./mt5-small/tokenizer')
print('✅ Model downloaded successfully!')
"
cd ../..
```

### 4. Run Everything with Docker

```bash
docker compose up --build
```

**Services will be available at:**
- Backend (Next.js): http://localhost:3000
- OCR Service: http://localhost:8000
- AI LLM Service: http://localhost:8001

---

## 🌿 Daily Workflow

### Starting Work

```bash
# 1. Update develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-task-name

# 3. Start Docker
docker compose up
```

### Making Changes

```bash
# Work on your feature...
# Test with Docker running

# Before committing, ensure no conflicts
git fetch origin
git merge develop

# Test again
docker compose up

# Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-task-name
```

### Creating Pull Request

1. Go to GitHub
2. Create PR from `feature/your-task-name` → `develop`
3. Request review from team member
4. Wait for approval
5. Merge to develop

⚠️ **NEVER push directly to `main` or `develop`**

---

## 🐳 Docker Commands

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Rebuild after changes
docker compose up --build

# Stop all services
docker compose down

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend

# Restart single service
docker compose restart ocr-service
```

---

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000
# Kill it
kill -9 <PID>
```

### Docker Build Fails

```bash
# Clean everything and rebuild
docker compose down -v
docker system prune -af
docker compose up --build
```

### Model Not Found Error

Make sure you downloaded the MT5 models (see Step 3 above).

### Git Conflicts

```bash
git checkout feature/your-branch
git fetch origin
git merge develop
# Fix conflicts manually
git add .
git commit -m "fix: resolve merge conflicts"
docker compose up  # Always test!
```

---

## 📁 Project Structure

```
DasTern/
├── backend-nextjs/          # Next.js API gateway
├── ocr-service/            # Python OCR service
├── ai-llm-service/         # Python AI/LLM service
├── mobile-flutter/         # Flutter mobile app
├── shared/                 # Shared types/constants
├── docs/                   # Documentation
├── docker-compose.yml      # Docker orchestration
└── .env                    # Environment variables (not in git)
```

---

## 🎯 Branch Strategy

- `main` - Production/Demo (protected)
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes

---

## 👥 Getting Help

1. Check this guide
2. Ask in team chat
3. Create GitHub issue
4. Contact team lead

---

## ✅ Ready to Code!

Once you complete all steps above, you're ready to contribute! 🎉
