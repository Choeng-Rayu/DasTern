# AI-LLM Service

AI-powered prescription OCR correction and parsing service using LLaMA 3.1 8B via Ollama.

## What This Does

Takes messy OCR output from prescription images and:
- **Corrects OCR errors** (s00mg → 500mg, Esome → Esomeprazole)
- **Extracts key medical data** (patient, medications, dosages, instructions)
- **Ignores irrelevant data** (IDs, phone numbers, layout artifacts)
- **Outputs clean JSON** for the DasTern mobile app

---

## Setup (First Time)

### 1. Install Ollama & Download Model

```bash
# Install Ollama
brew install ollama

# Start Ollama server (keep this running in one terminal)
ollama serve

# In another terminal, download LLaMA model (4.9GB, one-time download)
ollama pull llama3.1:8b

# Verify model is downloaded
ollama list
```

### 2. Setup Python Environment

```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) prefix in your terminal
# Install dependencies
pip install -r requirements.txt
```

### 3. Set Environment Variable

```bash
# Set this every time you open a new terminal
export OLLAMA_HOST=http://localhost:11434

# Or add to ~/.zshrc to make it permanent:
echo 'export OLLAMA_HOST=http://localhost:11434' >> ~/.zshrc
```

### 4. Verify Setup

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Should show: {"models":[{"name":"llama3.1:8b",...}]}

# Run test
python3 tests/test_simple.py
```

---

## Daily Usage

Every time you start working:

```bash
# 1. Make sure Ollama is running (in one terminal)
ollama serve

# 2. In your work terminal:
cd /Users/macbook/CADT/DasTern/ai-llm-service
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# Now you're ready to use the tools!
```

---

## How to Use

### Process OCR Data

```bash
# Process a prescription OCR file
python3 tools/process_with_corrections.py data/ocr_file.json
```

**Input format** (your OCR JSON):
```json
{
  "corrected_text": "Dr. Sun Moniroth\nPatient: Mr. Pich\nparacetamo1 s00mg...",
  "raw": [...],
  "stats": {...}
}
```

**Output:** Generates `reports/correction_report_YYYYMMDD_HHMMSS.json` with:
- Original OCR text
- AI-enhanced output
- All corrections made
- Quality metrics

### Add Training Data (Teach the AI)

**When to use:** AI makes mistakes on a new hospital format

**What you need:** The original prescription **image** (not just OCR output)

**How it works:**

```bash
python3 tools/add_training_simple.py data/new_prescription.json
```

**The tool will:**
1. Show you the messy OCR text
2. Ask YOU (human) to type the CORRECT data by looking at the original image
3. Save this example so AI learns the pattern

**Example session:**
```
📄 OCR Text (messy):
paracetamo1 s00mg
Patient: 25 years

Now YOU look at the original image and type correct data:

Patient name? Mr. Pich Chan
Patient age? 35
Medication name? Paracetamol
Medication strength? 500mg
...
```

**How AI "learns":**
- ✅ NO model retraining required
- ✅ Uses **few-shot learning** - includes your examples in every prompt
- ✅ Instant - works immediately after adding example
- ✅ Just needs 3-5 examples to handle most cases

**Your examples are saved in:** `data/training/sample_prescriptions.jsonl`

### Run Tests

```bash
# Test with real OCR data
python3 tests/test_real_ocr_data.py

# Quick API test
python3 tests/test_simple.py
```

---

## Project Structure

```
ai-llm-service/
├── tools/                        # User scripts
│   ├── add_training_simple.py    # Add training examples
│   └── process_with_corrections.py # Process OCR files
├── tests/                        # Test scripts
│   ├── test_real_ocr_data.py     # Test with real data
│   └── test_simple.py            # Quick API test
├── app/                          # Core application
│   ├── main.py                   # FastAPI server
│   ├── core/                     # AI generation & model loading
│   ├── features/prescription/    # Prescription enhancer & validator
│   └── safety/                   # Safety checks
├── prompts/                      # AI system prompts
│   └── medical_system_prompt.py  # Instructions for LLaMA
├── data/                         # Data files
│   └── training/sample_prescriptions.jsonl  # Training examples
├── reports/                      # Generated outputs (gitignored)
└── requirements.txt              # Python dependencies
```

---

## Common Tasks

### Daily Workflow

```bash
# 1. Start working
cd /Users/macbook/CADT/DasTern/ai-llm-service
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# 2. Process prescriptions
python3 tools/process_with_corrections.py data/prescription1.json
python3 tools/process_with_corrections.py data/prescription2.json

# 3. Check reports
ls -lh reports/
cat reports/correction_report_*.json | jq
```

### Add New Hospital Format (Step-by-Step)

**Scenario:** You receive OCR from a new hospital and AI makes mistakes.

**Step 1: Test current AI**
```bash
python3 tools/process_with_corrections.py data/new_hospital.json
```

Check `reports/` - is the output correct?
- ✅ If correct → Done! No training needed
- ❌ If wrong → Continue to Step 2

**Step 2: Add training example**

You need:
1. The OCR JSON file (`new_hospital.json`)
2. The **original prescription image** (to read correct data)

```bash
python3 tools/add_training_simple.py data/new_hospital.json
```

**Step 3: Look at the image and type correct data**

Tool shows messy OCR, you type what you **see in the image**:
```
Patient name? [Look at image, type: "លោក ពេជ្រ ចន្ទ"]
Age? [Look at image, type: "35"]
Medication? [Look at image, type: "Paracetamol"]
Strength? [Look at image, type: "500mg"]
```

**Step 4: Test again**
```bash
python3 tools/process_with_corrections.py data/similar_prescription.json
```

AI now knows the pattern and will handle similar formats correctly!

### Update AI Behavior

Edit `prompts/medical_system_prompt.py`:
- Add new medication name patterns
- Add new OCR error corrections
- Update extraction rules

### View Generated Reports

```bash
# List all reports
ls -lh reports/

# View specific report (with jq for pretty formatting)
cat reports/correction_report_20260128_204805.json | jq

# Or without jq
cat reports/correction_report_20260128_204805.json
```

---

## Troubleshooting

**Ollama not responding:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

**Model not found:**
```bash
# List installed models
ollama list

# Pull LLaMA if missing
ollama pull llama3.1:8b
```

**Import errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies if needed
pip install -r requirements.txt
```

**"venv/bin/activate: No such file":**
```bash
# You need to create venv first
python3 -m venv venv

# Then activate it
source venv/bin/activate
```

**Wrong Python version:**
```bash
# Check Python version (should be 3.8+)
python3 --version

# Use python3 explicitly
python3 tools/process_with_corrections.py data/file.json
```

---

## How Few-Shot Learning Works

**NOT traditional training** - no model updates, no GPU needed!

**What happens when you add training:**
1. Your example is saved to `data/training/sample_prescriptions.jsonl`
2. Every time AI processes OCR, it reads these examples
3. AI sees the pattern and mimics it

**Example:**

Before adding training:
```
AI sees: "paracetamo1 s00mg"
AI output: Confused, might fail
```

After adding ONE example:
```
Prompt to AI:
"Example: paracetamo1 s00mg → Paracetamol 500mg
Now process: Esome praso1 40mg"

AI output: Esomeprazole 40mg ✓
```

**Key points:**
- ✅ Works instantly (no training time)
- ✅ 3-5 examples usually enough
- ✅ No GPU needed
- ✅ Model stays the same (llama3.1:8b)

---

## Training Examples

Training data location: `data/training/sample_prescriptions.jsonl`

Current examples:
1. Khmer prescription (Calmette Hospital)
2. Mixed language prescription
3. English prescription
4. Messy OCR (Khmer-Soviet Hospital) with corrections

Add more using `tools/add_training_simple.py`

---

## Docker Deployment

```bash
# Build image
docker build -t ai-llm-service .

# Run container
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  ai-llm-service
```

---

## For Your Teammates

Three options for using this AI service:

### Option 1: Local Ollama (Recommended)
Everyone installs Ollama and downloads the model:
```bash
brew install ollama
ollama pull llama3.1:8b  # 4.9GB download per person
ollama serve
```
**Pros:** Fast (local), works offline  
**Cons:** 5GB storage per person

### Option 2: Shared Server
One person hosts Ollama, others connect remotely:
```bash
# Host machine (you):
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# Teammates:
export OLLAMA_HOST=http://YOUR_IP:11434
python3 tools/process_with_corrections.py data/file.json
```
**Pros:** No model download for teammates  
**Cons:** Your machine must stay running

### Option 3: Docker
Package everything in Docker (see Docker Deployment section)

---

## Tips

- **Environment variables:** Always set `OLLAMA_HOST` before running scripts
- **Virtual environment:** Always activate with `source venv/bin/activate`
- **Training:** Start with 3-5 examples, add more as needed
- **Testing:** Use `test_real_ocr_data.py` to verify improvements
- **Reports:** Check `reports/` folder for detailed correction analysis
- **Original images:** Keep prescription images to add training examples later

### **Check Current Training Examples**
```bash
# View all examples
cat data/training/sample_prescriptions.jsonl | jq
```

### **Run All Tests**
```bash
cd tests/
python3 test_simple.py
python3 test_phase2.py
python3 test_real_ocr_data.py
```

---

## 🎯 Workflow Summary

```
1. Get OCR JSON from your system
   ↓
2. Process with AI
   python3 tools/process_with_corrections.py data/ocr.json
   ↓
3. Check accuracy in reports/
   ↓
4. If accuracy low (<85%), add training example
   python3 tools/add_training_simple.py data/ocr.json
   ↓
5. Process again - accuracy improves!
```

---

## 🆘 Need Help?

- **Setup issues:** See `docs/TESTING_GUIDE.md`
- **How to use tools:** See `docs/QUICK_REFERENCE.md`
- **Understanding corrections:** Check `reports/correction_report_*.json`

---

## 📞 Quick Commands

```bash
# Setup
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# Add training
python3 tools/add_training_simple.py <ocr.json>

# Process OCR
python3 tools/process_with_corrections.py <ocr.json>

# Test
python3 tests/test_real_ocr_data.py
```

---

**Everything is organized and ready to use!** 🚀
=======
# ai-llm-service

MT5-based FastAPI service for OCR correction and chat.

## Prerequisites
- Python 3.10+
- (Optional) GPU drivers/CUDA for faster inference

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Open:
- API docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

## Endpoints
- POST /api/v1/correct
- POST /api/v1/chat

## Notes
- The MT5 model is downloaded on first run (can take time and disk space).
>>>>>>> 37d6bba29275ae1bbf219be386ab684374815fad
