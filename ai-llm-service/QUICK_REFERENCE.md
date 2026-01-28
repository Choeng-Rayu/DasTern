# 📚 Quick Reference: Training & Correction Reports

## 🎓 How to Add Training Examples

Training examples teach LLaMA how to parse different prescription formats. Each example shows:
- **Input**: Raw, messy OCR text
- **Output**: Clean, structured JSON

### **Method 1: Interactive Tool (Recommended)**

```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service
source venv/bin/activate
python3 add_training_example.py
```

**What it does:**
- Guides you step-by-step to add new examples
- Provides templates for common hospitals
- Automatically formats and saves to `data/training/sample_prescriptions.jsonl`

**Example session:**
```
📝 Step 1: Enter RAW OCR TEXT (messy input)
Paste the raw OCR text, then press Enter twice:
----------------------------------------------------------------------
Khmer-Soviet Hospital
Patient: 25 years
paracetamo1 s00mg
[Press Enter twice]

📝 Step 2: Enter EXPECTED JSON OUTPUT
Options:
  1. Paste JSON directly
  2. Use template (recommended)

Choice: 2

Patient name: [leave blank]
Patient age: 25
Gender: [leave blank]
...
```

---

### **Method 2: Quick Templates**

```bash
python3 add_training_example.py
# Choose option 2: Quick add (from templates)
```

Templates available:
- Khmer-Soviet Friendship Hospital (messy OCR)
- Calmette Hospital (Khmer text)
- Custom (manual entry)

---

### **Method 3: Edit File Directly**

Edit `data/training/sample_prescriptions.jsonl`:

```jsonl
{"user": "Your raw OCR text here...", "assistant": "{\"age\": 25, \"medications\": [...]}"}
```

**Format rules:**
- One example per line
- Must be valid JSON
- Use `\n` for line breaks in text
- Use `\"` to escape quotes inside strings

**Example:**
```jsonl
{"user": "Soviet Hospital\nHAKF123456\nAge: 19\nChronic Cystitis\nButylscopolamine 14 days\nEsome 20mg", "assistant": "{\"age\": 19, \"prescriber_facility\": \"Khmer-Soviet Friendship Hospital\", \"diagnosis\": \"Chronic Cystitis\", \"medications\": [{\"medication_name\": \"Butylscopolamine\", \"duration_days\": 14}, {\"medication_name\": \"Esomeprazole\", \"strength\": \"20mg\"}]}"}
```

---

## 📊 How to See Corrections Made

### **Generate Detailed Correction Report**

```bash
cd /Users/macbook/CADT/DasTern/ai-llm-service
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# Process your OCR file and get correction report
python3 process_with_corrections.py data/ocr_test_image2_20260127_162549.json
```

**Output:** `correction_report_YYYYMMDD_HHMMSS.json`

**What's in the report:**
```json
{
  "report_metadata": {
    "generated_at": "2026-01-28T...",
    "model": "LLaMA 3.1 8B via Ollama"
  },
  
  "ocr_input": {
    "raw_text": "oviet Hospital HAKF1354164...",
    "overall_confidence": 70.86,
    "low_confidence_blocks": 32
  },
  
  "ai_enhanced_output": {
    "age": 19,
    "prescriber_facility": "Khmer-Soviet Friendship Hospital",
    "diagnosis": "Chronic Cystitis",
    "medications": [...]
  },
  
  "corrections_made": {
    "total_corrections": 6,
    "by_type": {
      "medication_name": 2,
      "dosage_strength": 1,
      "ignored_data": 3
    },
    "details": [
      {
        "type": "medication_name",
        "original": "Esome",
        "corrected": "Esomeprazole",
        "reason": "OCR spelling error correction"
      },
      {
        "type": "dosage_strength",
        "original": "s00mg",
        "corrected": "500mg",
        "reason": "OCR number/letter confusion"
      },
      {
        "type": "ignored_data",
        "original": "HAKF1354164",
        "corrected": null,
        "reason": "Prescription ID numbers (intentionally ignored)"
      }
    ]
  },
  
  "quality_metrics": {
    "input_confidence": 70.86,
    "output_confidence": 85.0,
    "improvement": 14.14,
    "corrections_made": 6,
    "data_completeness": 83.3
  }
}
```

---

## 🔄 Complete Workflow

### **1. When You Get New Prescription Data:**

```bash
# Step 1: Process and generate correction report
python3 process_with_corrections.py new_ocr_data.json my_report.json

# Step 2: Review the corrections
cat my_report.json

# Step 3: If accuracy is good (>85%), you're done!
# If accuracy is low (<85%), add as training example...
```

---

### **2. If Accuracy Needs Improvement:**

```bash
# Add the prescription as a training example
python3 add_training_example.py

# Paste the raw OCR text
# Enter the correct structured output
# Save

# The next time you process similar prescriptions, accuracy will improve!
```

---

### **3. Testing Your Improvements:**

```bash
# After adding training examples, test again
python3 process_with_corrections.py data/ocr_test_image2_20260127_162549.json test_after_training.json

# Compare before/after reports
diff correction_report_before.json test_after_training.json
```

---

## 📁 File Structure

```
ai-llm-service/
├── add_training_example.py          ← Add new training examples
├── process_with_corrections.py      ← Generate correction reports
├── data/
│   └── training/
│       └── sample_prescriptions.jsonl  ← Training examples (editable)
├── correction_report_*.json         ← Generated reports
└── QUICK_REFERENCE.md              ← This file
```

---

## 💡 Tips

### **When to Add Training Examples:**
- ✅ New hospital format you haven't seen before
- ✅ Accuracy drops below 85% on specific prescription type
- ✅ Common OCR errors that aren't being corrected
- ✅ Unique medication names or terminology

### **How Many Examples Needed:**
- **2-3 examples** per hospital format is usually enough
- **Total 10-20 examples** covers most cases
- More examples = better accuracy, but diminishing returns after 20

### **Best Practices:**
1. **Use real OCR data** - Don't make up examples
2. **Include variety** - Different doctors, dates, medications
3. **Keep it messy** - Include OCR errors in the input
4. **Be accurate** - Output should be perfect, corrected data
5. **Test immediately** - After adding examples, test with similar data

---

## 🚀 Quick Commands Cheat Sheet

```bash
# Activate environment
cd /Users/macbook/CADT/DasTern/ai-llm-service
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434

# Add training example (interactive)
python3 add_training_example.py

# Process OCR and get corrections
python3 process_with_corrections.py <input.json> [output.json]

# View training examples
cat data/training/sample_prescriptions.jsonl | jq

# Count training examples
wc -l data/training/sample_prescriptions.jsonl

# Test with real OCR data
python3 test_real_ocr_data.py
```

---

## 📊 Example Output

### **Terminal Output:**
```
================================================================================
  📊 OCR CORRECTION REPORT GENERATOR
================================================================================

📂 Loading: data/ocr_test_image2_20260127_162549.json
✅ Loaded 500 characters of OCR text
   Confidence: 70.9%
   Low confidence blocks: 32

🤖 Processing with AI (this takes 4-5 seconds)...
✅ AI processing complete

🔍 Analyzing corrections...
✅ Detected 6 corrections

💾 Report saved: correction_report_20260128_143022.json

================================================================================
  📈 CORRECTION SUMMARY
================================================================================

🔴 INPUT (Raw OCR):
   • Confidence: 70.9%
   • Low quality blocks: 32
   • Needs review: True

🟢 OUTPUT (AI Enhanced):
   • Confidence: 85.0%
   • Medications extracted: 4
   • Data completeness: 83.3%

🔧 CORRECTIONS MADE: 6
   • Medication Name: 2
   • Dosage Strength: 1
   • Ignored Data: 3

📝 CORRECTION DETAILS:
   1. Esome → Esomeprazole
      Reason: OCR spelling error correction
   2. s00mg → 500mg
      Reason: OCR number/letter confusion
   3. HAKF1354164 → [IGNORED]
      Reason: Prescription ID numbers (intentionally ignored)
   ... and 3 more corrections

✅ Full report saved to: correction_report_20260128_143022.json
```

---

## 🎯 Summary

| Task | Command | Output |
|------|---------|--------|
| **Add training** | `python3 add_training_example.py` | Updates `sample_prescriptions.jsonl` |
| **See corrections** | `python3 process_with_corrections.py <file>` | Generates `correction_report_*.json` |
| **Test accuracy** | `python3 test_real_ocr_data.py` | Terminal output + result JSON |

Your AI service learns from examples and gets better with each addition! 🚀
