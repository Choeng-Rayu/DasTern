<<<<<<< HEAD
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
# Install Ollama (if not installed)
brew install ollama

# Start Ollama server
ollama serve

# Download LLaMA model (in another terminal)
ollama pull llama3.1:8b
```

### 2. Setup Python Environment

```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set Ollama host
export OLLAMA_HOST=http://localhost:11434
```

### 3. Verify Setup

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Run test
python3 tests/test_simple.py
```

---

## How to Use

### Process OCR Data

```bash
# Activate environment first
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# Process a prescription OCR file
python3 tools/process_with_corrections.py data/my_prescription.json
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

### Add Training Data

When you get new prescription formats:

```bash
python3 tools/add_training_simple.py data/new_prescription.json
```

**Interactive steps:**
1. Tool loads your OCR JSON
2. You provide correct extracted data
3. Saves to `data/training/sample_prescriptions.jsonl`
4. AI learns from it automatically

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

### Add New Hospital Format

```bash
# When you get OCR from a new hospital
python3 tools/add_training_simple.py data/new_hospital_ocr.json

# Follow prompts to enter correct data
# AI will learn this format
```

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

**Wrong Python version:**
```bash
# Check Python version (should be 3.8+)
python3 --version

# Use python3 explicitly
python3 tools/process_with_corrections.py data/file.json
```

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

## Tips

- **Environment variables:** Always set `OLLAMA_HOST` before running scripts
- **Virtual environment:** Always activate with `source venv/bin/activate`
- **Training:** Start with 3-5 examples, add more as needed
- **Testing:** Use `test_real_ocr_data.py` to verify improvements
- **Reports:** Check `reports/` folder for detailed correction analysis
```bash
# From your OCR JSON
python3 tools/add_training_simple.py data/new_prescription.json
```

### **Process New Prescription**
```bash
# Generate correction report
python3 tools/process_with_corrections.py data/new_ocr.json
```

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
