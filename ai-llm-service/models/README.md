# MT5 Quick Start Guide

## 📖 What You Now Have

1. **Comprehensive Guide**: [ai/MT5_GUIDE.md](MT5_GUIDE.md) - Complete documentation
2. **Demo Script**: [ai/demo_mt5.py](demo_mt5.py) - Interactive examples
3. **Training Script**: [ai/fine_tune/train_mt5.py](fine_tune/train_mt5.py) - Fine-tune on your data
4. **Sample Data**: [ai/fine_tune/sample_training_data.json](fine_tune/sample_training_data.json) - Example training format

---

## 🚀 Quick Start

### 1. Test the MT5 Model (Demo)

```bash
cd /home/rayu/DasTern/OCR_System/ocr-backend/ai
/home/rayu/DasTern/.venv/bin/python demo_mt5.py
```

This will show you:
- Basic correction examples
- Batch processing
- Language detection
- Parameter tuning
- Medical prescription examples
- Interactive mode

### 2. Use MT5 in Your Code

```python
from app.ai_corrector import ai_correct

# Fix OCR errors
noisy = "paracetamo1 500 rng 2 x daY"
clean = ai_correct(noisy, lang="eng")
# Result: "Paracetamol 500mg, twice daily"
```

### 3. Train on Your Own Data

**Step 1:** Create training data file:

```json
[
  {
    "lang": "eng",
    "input": "your_ocr_error_text",
    "output": "corrected_text"
  }
]
```

**Step 2:** Run training:

```bash
cd /home/rayu/DasTern/OCR_System/ocr-backend/ai/fine_tune

/home/rayu/DasTern/.venv/bin/python train_mt5.py \
    --data_path ./my_data.json \
    --epochs 3 \
    --batch_size 4
```

**Step 3:** The trained model will be saved to `ai/mt5/model/` and automatically used

---

## 📊 How It Works

```
┌─────────────────────────────────────────────┐
│  Your Prescription Image                    │
│  ┌───────────────────────────────────────┐ │
│  │ Patient: John Doe                     │ │
│  │ RX: paracetamo1 500 rng 2x daily     │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  Tesseract OCR        │ ← Extracts text
        └───────────────────────┘
                    ↓
        "paracetamo1 500 rng 2x daily" ← Raw (has errors)
                    ↓
        ┌───────────────────────┐
        │  MT5 AI Correction    │ ← Fixes errors
        └───────────────────────┘
                    ↓
        "Paracetamol 500mg twice daily" ← Clean ✅
```

**Key Point:** MT5 doesn't do OCR - it fixes OCR errors!

---

## 🎯 Common Use Cases

### 1. Fix Common OCR Errors

```python
# Numbers mistaken for letters
"0" → "O", "1" → "l", "5" → "S"

# Letters mistaken for numbers  
"O" → "0", "l" → "1", "S" → "5"

# Character combinations
"rn" → "m", "cl" → "d", "vv" → "w"
```

### 2. Medical Terminology

```python
# Abbreviations
"para" → "Paracetamol"
"amox" → "Amoxicillin"

# Dosage formats
"500 rng" → "500mg"
"2x daily" → "twice daily"
"3 tirnes" → "3 times"
```

### 3. Multi-Language Prescriptions

```python
# English
"take 1 tab1et after mea1s"
→ "Take 1 tablet after meals"

# Khmer
"ថ្នាំ បញ្ចុះ កម្ដៅ"
→ "ថ្នាំបញ្ចុះកម្ដៅ"

# French
"comprimé 2x par jour"
→ "comprimé 2 fois par jour"
```

---

## ⚙️ Configuration

### In Your OCR Pipeline

Edit `app/main.py` to enable/disable AI correction:

```python
@app.post("/ocr")
async def process_image(
    file: UploadFile = File(...),
    use_ai_correction: bool = Form(default=True),  # ← Toggle here
    ...
):
```

### Performance Tuning

Edit `app/ai_corrector.py`:

```python
def ai_correct(text, lang="eng", num_beams=4):
    # num_beams: 1 (fast) → 4 (balanced) → 8 (best quality)
```

---

## 📈 Training Tips

### Collect Good Training Data

1. **Real OCR Errors**: Process actual prescription images
2. **Manual Corrections**: Have humans fix the errors
3. **Minimum**: 100 examples per language
4. **Recommended**: 1,000-5,000 examples
5. **Professional**: 10,000+ examples

### Data Format

```json
[
  {"lang": "eng", "input": "error_text", "output": "correct_text"},
  {"lang": "eng", "input": "more_errors", "output": "more_corrections"},
  ...
]
```

### Training Time

- **100 samples**: ~10 minutes (CPU)
- **1,000 samples**: ~1-2 hours (CPU)
- **10,000 samples**: ~10-20 hours (CPU)

With GPU: 5-10x faster

---

## 🔍 Testing Your Model

### A/B Comparison

```bash
# Test with AI correction
curl -X POST http://localhost:8000/ocr \
  -F "file=@prescription.jpg" \
  -F "use_ai_correction=true"

# Test without AI correction
curl -X POST http://localhost:8000/ocr \
  -F "file=@prescription.jpg" \
  -F "use_ai_correction=false"
```

Compare the results!

---

## 📚 Learn More

1. **Full Guide**: [ai/MT5_GUIDE.md](MT5_GUIDE.md)
2. **Run Demo**: `python ai/demo_mt5.py`
3. **Training Code**: [ai/fine_tune/train_mt5.py](fine_tune/train_mt5.py)
4. **Corrector Code**: [app/ai_corrector.py](../app/ai_corrector.py)

---

## 🆘 Troubleshooting

### Model Download Issues

```bash
# Manually download MT5
cd /home/rayu/DasTern/OCR_System/ocr-backend/ai/fine_tune
/home/rayu/DasTern/.venv/bin/python -c "
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
tokenizer = MT5Tokenizer.from_pretrained('google/mt5-small')
model = MT5ForConditionalGeneration.from_pretrained('google/mt5-small')
tokenizer.save_pretrained('../mt5/tokenizer')
model.save_pretrained('../mt5/model')
print('✅ Model downloaded!')
"
```

### Out of Memory

- Reduce `batch_size` in training (4 → 2 → 1)
- Use `num_beams=1` for faster inference
- Process texts one at a time instead of batches

### Poor Quality

- Collect more training data
- Increase `num_beams` (4 → 8)
- Train for more epochs (3 → 5-10)

---

## 💡 Key Takeaways

✅ **MT5 is for correction**, not OCR itself  
✅ **Works offline** after first download  
✅ **Multilingual** - English, Khmer, French  
✅ **CPU-friendly** - no GPU required  
✅ **Fine-tunable** - train on your data  
✅ **Easy to use** - just call `ai_correct(text)`  

---

**Ready to start?**

1. Run the demo: `python ai/demo_mt5.py`
2. Read the guide: [ai/MT5_GUIDE.md](MT5_GUIDE.md)
3. Train your model: `python ai/fine_tune/train_mt5.py`

Good luck! 🚀
