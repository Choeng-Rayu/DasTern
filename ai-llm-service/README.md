# 🗂️ AI-LLM Service - Clean Folder Structure

## 📁 Directory Organization

```
ai-llm-service/
├── 📦 tools/              # User-facing tools (run these!)
├── 🧪 tests/              # Test scripts and demos
├── 📚 docs/               # Documentation
├── 📊 reports/            # Generated outputs (gitignored)
├── 🔧 app/                # Core application code
├── 💬 prompts/            # AI system prompts
├── 📁 data/               # Training data and OCR files
├── 🐍 venv/               # Python virtual environment
├── 📄 requirements.txt    # Python dependencies
├── 🐳 Dockerfile          # Docker configuration
└── 📖 README.md           # This file
```

---

## 🚀 Quick Start

### **1. Setup (First Time Only)**
```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies  
pip install -r requirements.txt
```

### **2. Daily Usage**
```bash
# Activate environment
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# Add training examples
python3 tools/add_training_simple.py data/my_ocr.json

# Process OCR and see corrections
python3 tools/process_with_corrections.py data/my_ocr.json

# Run tests
python3 tests/test_real_ocr_data.py
```

---

## 📦 Tools (Main Scripts You Use)

### **`tools/add_training_simple.py`**
Add training examples from your OCR JSON files.

**Usage:**
```bash
python3 tools/add_training_simple.py data/prescription.json
```

**What it does:**
- Reads your OCR JSON (with `corrected_text` field)
- Guides you to enter correct extracted data
- Saves as training example for AI to learn

---

### **`tools/process_with_corrections.py`**
Process OCR data and generate detailed correction reports.

**Usage:**
```bash
python3 tools/process_with_corrections.py data/ocr_file.json [output.json]
```

**What it does:**
- Takes messy OCR input
- AI processes and cleans it
- Shows all corrections made
- Generates JSON report in `reports/`

**Output:** `reports/correction_report_YYYYMMDD_HHMMSS.json`

---

## 🧪 Tests (Test Scripts)

### **`tests/test_real_ocr_data.py`**
Test with real OCR data file.

```bash
python3 tests/test_real_ocr_data.py
```

### **`tests/test_simple.py`**
Quick API test.

```bash
python3 tests/test_simple.py
```

### **`tests/test_phase2.py`**
Full prescription enhancement test.

```bash
python3 tests/test_phase2.py
```

### **`tests/demo_showcase.sh`**
Complete demo script.

```bash
./tests/demo_showcase.sh
```

---

## 📚 Documentation (Read These!)

### **`docs/QUICK_REFERENCE.md`**
- How to add training examples
- How to see corrections
- Quick command reference

### **`docs/TESTING_GUIDE.md`**
- Complete setup instructions
- Testing procedures  
- Troubleshooting

### **`docs/DAILY_PROGRESS_SHOWCASE.md`**
- Project progress tracking
- Feature demonstrations

---

## 📊 Reports (Auto-Generated)

The `reports/` folder contains:
- `correction_report_*.json` - Detailed correction analysis
- `test_result*.json` - Test outputs

**Note:** This folder is gitignored. Reports are temporary and regenerated.

---

## 🔧 Application Code

### **`app/`** - Core Service
```
app/
├── main.py                    # FastAPI service
├── core/
│   ├── generation.py          # LLaMA generation logic
│   └── model_loader.py        # Ollama connection
├── features/
│   └── prescription/
│       ├── enhancer.py        # Main enhancement logic
│       └── validator.py       # Validation rules
└── safety/
    ├── language.py            # Language detection
    └── medical.py             # Medical safety checks
```

### **`prompts/`** - AI Instructions
```
prompts/
└── medical_system_prompt.py   # System prompt for LLaMA
```

### **`data/`** - Data Files
```
data/
├── training/
│   └── sample_prescriptions.jsonl  # Training examples (editable!)
├── labeled/                    # Labeled data (if any)
└── raw/                        # Raw OCR outputs
```

---

## 🧹 Cleanup Complete!

### **Files Moved:**
- ✅ Tools → `tools/`
- ✅ Tests → `tests/`
- ✅ Docs → `docs/`
- ✅ Reports → `reports/`

### **Files Removed:**
- 🗑️ `add_training_example.py` (old complex version)
- 🗑️ `cleanup_and_reorganize.sh` (cleanup script itself)
- 🗑️ `reorganize.py` (cleanup script)

---

## 📝 Common Tasks

### **Add More Training Examples**
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
