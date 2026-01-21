# 🎬 Live Testing with Real-Time Logs

Complete guide to view live logs while testing your services.

---

## 🎯 Setup: Two Terminal Windows

### **Terminal 1: Watch Logs**
```bash
cd /home/rayu/DasTern
sudo docker compose logs -f
```
This shows **live logs** from all services. Logs update as requests happen.

### **Terminal 2: Test Your Services**
```bash
cd /home/rayu/DasTern
# Run tests, make requests, etc.
curl http://localhost:3000
```

**Result**: Terminal 1 shows live updates as you test in Terminal 2!

---

## 📋 Step-by-Step Guide

### Step 1: Open First Terminal
```bash
cd /home/rayu/DasTern
```

### Step 2: Start Watching Logs
```bash
sudo docker compose logs -f
```

Output shows (continuously updating):
```
dastern-backend  | ✓ Ready in 1568ms
dastern-ocr      | INFO: Application startup complete
dastern-ai       | INFO: Uvicorn running on 0.0.0.0:8001
```

### Step 3: Open Second Terminal (Keep first one open!)
```bash
# Do NOT close Terminal 1!
# Open a new terminal window/tab
cd /home/rayu/DasTern
```

### Step 4: Test in Second Terminal
```bash
# Make a request
curl http://localhost:3000

# Or test OCR service
curl http://localhost:8000/docs

# Or test AI service  
curl http://localhost:8001/docs
```

### Step 5: Watch Terminal 1
You'll see **live logs** appear in real-time:
```
dastern-backend  | GET / 200 in 70ms
dastern-backend  | GET /_next/static/... 200 in 5ms
```

---

## 🖥️ Better Approach: Split Terminals

Instead of two separate windows, use split terminal in VS Code:

### In VS Code:
1. Open Terminal (Ctrl+`)
2. Click Split Terminal icon (or Ctrl+Shift+5)
3. Now you have LEFT and RIGHT terminals

**LEFT Terminal:**
```bash
cd /home/rayu/DasTern
sudo docker compose logs -f
```

**RIGHT Terminal:**
```bash
cd /home/rayu/DasTern
# Run tests here
curl http://localhost:3000
```

**Result**: Watch logs on LEFT while testing on RIGHT! 🎯

---

## 📊 Watch Specific Service Only

### Watch Backend While Testing

**Terminal 1:**
```bash
sudo docker compose logs -f backend
```

**Terminal 2:**
```bash
# Test backend
curl http://localhost:3000
```

**See Live Logs:**
```
dastern-backend  | GET / 200 in 70ms
dastern-backend  | POST /api/ocr 201 in 150ms
dastern-backend  | GET /api/results 200 in 20ms
```

### Watch OCR Service While Testing

**Terminal 1:**
```bash
sudo docker compose logs -f ocr-service
```

**Terminal 2:**
```bash
# Send image to OCR
curl -X POST http://localhost:8000/process \
  -F "file=@image.jpg"
```

**See Live Logs:**
```
dastern-ocr  | INFO: Processing image
dastern-ocr  | INFO: Image quality: 95%
dastern-ocr  | INFO: OCR complete in 234ms
```

### Watch AI Service While Testing

**Terminal 1:**
```bash
sudo docker compose logs -f ai-llm-service
```

**Terminal 2:**
```bash
# Test AI correction
curl -X POST http://localhost:8001/correct \
  -H "Content-Type: application/json" \
  -d '{"text": "paracetamol 500mg"}'
```

**See Live Logs:**
```
dastern-ai  | INFO: Correcting text
dastern-ai  | INFO: Language detected: English
dastern-ai  | INFO: Result: Paracetamol 500mg
```

---

## 🔍 Watch All Services with Timestamps

**Terminal 1:**
```bash
sudo docker compose logs -ft
```

Output shows timestamps:
```
2026-01-19T10:30:45.123Z dastern-backend  | GET / 200 in 70ms
2026-01-19T10:30:46.456Z dastern-ocr      | INFO: Processing...
2026-01-19T10:30:47.789Z dastern-ai       | INFO: Complete
```

---

## 💡 Advanced: Watch Multiple Services

### Watch Backend + OCR Together

**Terminal 1:**
```bash
sudo docker compose logs -f backend ocr-service
```

Shows logs from both services:
```
dastern-backend  | POST /api/ocr from user
dastern-ocr      | Processing image...
dastern-ocr      | Complete!
dastern-backend  | Response sent to user
```

### Watch Backend + AI Together

**Terminal 1:**
```bash
sudo docker compose logs -f backend ai-llm-service
```

---

## 🎬 Real Testing Scenarios

### Scenario 1: Test OCR Pipeline

**Terminal 1 (Watch All):**
```bash
sudo docker compose logs -f
```

**Terminal 2 (Test):**
```bash
# Send image for OCR
curl -X POST http://localhost:3000/api/ocr \
  -F "image=@prescription.jpg"
```

**See in Terminal 1:**
```
dastern-backend  | POST /api/ocr - Starting processing
dastern-ocr      | Receiving image...
dastern-ocr      | Preprocessing image...
dastern-ocr      | Running Tesseract OCR...
dastern-ocr      | Confidence: 0.92
dastern-backend  | Received OCR result
dastern-backend  | Sending to AI service...
dastern-ai       | Correcting text...
dastern-ai       | Result ready
dastern-backend  | Response sent: 200 OK
```

### Scenario 2: Test Error Handling

**Terminal 1 (Watch Backend):**
```bash
sudo docker compose logs -f backend
```

**Terminal 2 (Send Bad Request):**
```bash
# Missing required field
curl -X POST http://localhost:3000/api/process \
  -H "Content-Type: application/json" \
  -d '{}'
```

**See in Terminal 1:**
```
dastern-backend  | POST /api/process
dastern-backend  | ERROR: Missing required field: image
dastern-backend  | Response: 400 Bad Request
```

### Scenario 3: Monitor Performance

**Terminal 1 (Watch Logs with Tail):**
```bash
sudo docker compose logs -f --tail=20
```

**Terminal 2 (Send Requests):**
```bash
# Multiple fast requests
for i in {1..5}; do
  curl http://localhost:3000
done
```

**See Response Times in Terminal 1:**
```
GET / 200 in 45ms
GET / 200 in 38ms
GET / 200 in 52ms
GET / 200 in 41ms
GET / 200 in 48ms
```

---

## ⚡ Quick Commands While Testing

### Monitor Resources (New Terminal)

```bash
# Watch CPU/Memory usage while testing
sudo docker stats

# Press Ctrl+C to stop
```

### Search Live Logs

**Terminal 1:**
```bash
sudo docker compose logs -f | grep -i error
```

Only shows ERROR lines in real-time!

### Save Live Logs to File

**Terminal 1:**
```bash
sudo docker compose logs -f > live_logs.txt &
# Runs in background

# Stop logging:
# fg (to bring to foreground)
# Ctrl+C
```

---

## 🎯 Recommended Setup for Development

### Three Terminals:

**Terminal 1 - Watch Logs:**
```bash
cd /home/rayu/DasTern
sudo docker compose logs -f
```

**Terminal 2 - Test/Code:**
```bash
# Make requests, edit code, run tests
curl http://localhost:3000
# Edit backend-nextjs/app/page.tsx
# Edit ocr-service/app/main.py
```

**Terminal 3 - Monitor Resources:**
```bash
sudo docker stats
```

Now you can:
- 👀 See logs on Terminal 1
- 🧪 Test on Terminal 2
- 📊 Monitor performance on Terminal 3

---

## 🔧 Useful Aliases (Optional)

Add these to your `.bashrc` or `.zshrc`:

```bash
alias dc='sudo docker compose'
alias dclog='sudo docker compose logs -f'
alias dclog-backend='sudo docker compose logs -f backend'
alias dclog-ocr='sudo docker compose logs -f ocr-service'
alias dclog-ai='sudo docker compose logs -f ai-llm-service'
alias dcstats='sudo docker stats'
alias dcps='sudo docker compose ps'
```

Then use:
```bash
dclog                   # View all logs
dclog-backend           # View backend logs
dcstats                 # Monitor resources
dcps                    # Check status
```

---

## 📝 Checklist: Live Testing Setup

- [ ] Terminal 1 open with `sudo docker compose logs -f`
- [ ] Terminal 2 ready for testing commands
- [ ] Both terminals visible (split or side-by-side)
- [ ] Services running (`sudo docker compose ps`)
- [ ] Ready to test!

---

## 🎓 Tips for Efficient Debugging

1. **Watch specific service**: Focus on the service you're testing
   ```bash
   sudo docker compose logs -f backend
   ```

2. **Add timestamps**: Helps track when issues happen
   ```bash
   sudo docker compose logs -f -t
   ```

3. **Filter by keywords**: Find specific events
   ```bash
   sudo docker compose logs -f | grep "error\|warning\|200\|500"
   ```

4. **Combine with grep**: Real-time filtering
   ```bash
   sudo docker compose logs -f | grep -i "post\|get"
   ```

5. **Save for analysis**: Keep a record of test runs
   ```bash
   sudo docker compose logs > test_run_$(date +%Y%m%d_%H%M%S).log
   ```

---

## ✅ You're Ready!

Now you can:
- ✓ View live logs while testing
- ✓ See exactly what each service is doing
- ✓ Quickly identify issues
- ✓ Monitor performance in real-time
- ✓ Track the full request flow

**Happy testing!** 🚀
