# 🤝 Contributing to DasTern

Thank you for contributing to DasTern! This guide will help you contribute effectively.

---

## 🎯 Before You Start

1. **Read the documentation:**
   - [README.md](README.md) - Architecture overview
   - [SETUP.md](SETUP.md) - Setup instructions
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick commands

2. **Setup your environment:**
   - Follow [SETUP.md](SETUP.md) completely
   - Ensure Docker works: `docker compose up`
   - Verify services are running

3. **Understand the architecture:**
   - Backend orchestrates everything
   - OCR service handles images only
   - AI service handles text only
   - Clear separation of concerns

---

## 🌿 Git Workflow (IMPORTANT)

### 1. Always Start from Develop

```bash
git checkout develop
git pull origin develop
```

### 2. Create Feature Branch

Use clear, descriptive names:

```bash
# Good examples:
git checkout -b feature/ocr-quality-check
git checkout -b feature/flutter-image-upload
git checkout -b fix/docker-port-conflict
git checkout -b docs/api-documentation

# Bad examples:
git checkout -b mywork
git checkout -b test
git checkout -b fix
```

### 3. Work on Your Feature

```bash
# Start Docker while working
docker compose up

# Make changes...
# Test frequently!

# Commit regularly with clear messages
git add .
git commit -m "feat: add image quality validation"
```

### 4. Before Creating PR

```bash
# Sync with develop
git fetch origin
git merge develop

# Resolve any conflicts
# Test everything!
docker compose up --build

# Push your branch
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub repository
2. Click "Pull requests" → "New pull request"
3. Select: `feature/your-feature` → `develop`
4. Write clear description:
   - What does this PR do?
   - How to test it?
   - Any breaking changes?
5. Request review from team member
6. Address review comments
7. After approval, merge to `develop`

---

## ✅ Commit Message Convention

Use semantic prefixes:

```bash
feat: add new feature
fix: bug fix
docs: documentation only
style: formatting, missing semicolons, etc.
refactor: code restructuring
test: adding tests
chore: maintenance tasks
```

**Examples:**
```bash
git commit -m "feat: implement OCR confidence scoring"
git commit -m "fix: resolve Docker port binding error"
git commit -m "docs: add API endpoint documentation"
git commit -m "refactor: simplify image preprocessing logic"
```

---

## 🐳 Docker Best Practices

### Always Use Docker for Development

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Rebuild after dependency changes
docker compose up --build
```

### Testing Your Changes

```bash
# Test locally with Docker
docker compose up

# Check all services are healthy
curl http://localhost:8000/health  # OCR
curl http://localhost:8001/health  # AI
curl http://localhost:3000/api/health  # Backend
```

### Clean Up When Needed

```bash
# Remove all containers
docker compose down

# Remove volumes too
docker compose down -v

# Clean everything
docker system prune -af
```

---

## 📝 Code Style Guidelines

### Python (OCR & AI Services)

- Use Black for formatting
- Follow PEP 8
- Type hints required
- Docstrings for functions

```python
def process_image(image_path: str, lang: str = "eng") -> dict:
    """
    Process image and extract text using OCR.
    
    Args:
        image_path: Path to image file
        lang: OCR language code (default: eng)
        
    Returns:
        Dictionary containing extracted text and confidence
    """
    # Implementation...
```

### TypeScript (Next.js Backend)

- Use ESLint + Prettier
- Follow Airbnb style guide
- Type everything explicitly
- No `any` types

```typescript
interface OcrResult {
  text: string;
  confidence: number;
  language: string;
}

async function processOcr(imagePath: string): Promise<OcrResult> {
  // Implementation...
}
```

### Dart (Flutter)

- Follow official Dart style guide
- Use `dart format`
- Meaningful variable names
- Document complex logic

---

## 🧪 Testing Requirements

Before submitting PR:

1. **Manual Testing:**
   - Test your feature with Docker
   - Test happy path
   - Test error cases
   - Test with different inputs

2. **Integration Testing:**
   - Verify service communication
   - Check API responses
   - Validate data flow

3. **Cross-Service Testing:**
   - If you changed OCR, test AI service still works
   - If you changed backend, test mobile app still works

---

## 🚫 What NOT to Do

❌ **Never push directly to `main` or `develop`**
❌ **Never commit `.env` files**
❌ **Never commit large model files** (use .gitignore)
❌ **Never force push to shared branches**
❌ **Never merge without testing in Docker**
❌ **Never commit `node_modules` or `__pycache__`**
❌ **Never use `git commit -m "update"` or "fix"**

---

## 🐛 Reporting Issues

When reporting bugs:

1. **Describe the problem clearly**
2. **Steps to reproduce**
3. **Expected vs actual behavior**
4. **Docker logs** (`docker compose logs`)
5. **Your environment** (OS, Docker version)

---

## 💡 Pro Tips

1. **Commit often:** Small, focused commits are easier to review
2. **Pull often:** Stay synced with develop to avoid big conflicts
3. **Test in Docker:** Always test in the same environment as production
4. **Ask questions:** Better to ask than break something
5. **Review others' code:** Learn from your teammates
6. **Keep PRs small:** Easier to review, faster to merge

---

## 📞 Getting Help

- **Technical issues:** Create GitHub issue
- **Quick questions:** Team chat
- **Workflow confusion:** Read this guide again
- **Setup problems:** Check [SETUP.md](SETUP.md)

---

## 🎓 Learning Resources

- [Docker Documentation](https://docs.docker.com/)
- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flutter Documentation](https://flutter.dev/docs)

---

## ✨ Thank You!

Your contributions make DasTern better. Happy coding! 🚀
