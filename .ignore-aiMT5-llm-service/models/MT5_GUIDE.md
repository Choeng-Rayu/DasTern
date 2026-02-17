# MT5 Model Guide for OCR Error Correction

## 📚 Table of Contents
1. [What is MT5?](#what-is-mt5)
2. [How It Works in This System](#how-it-works)
3. [Using the Model](#using-the-model)
4. [Customizing the Model](#customizing-the-model)
5. [Training Your Own Model](#training-your-own-model)
6. [Advanced Usage](#advanced-usage)

---

## What is MT5?

**MT5 (Multilingual T5)** is a text-to-text transformer model by Google that:
- Supports 101+ languages (including English, Khmer, French)
- Size: MT5-small has ~300M parameters (~1.2GB download)
- Can run on CPU (no GPU required)
- Purpose in this system: **OCR Error Correction** (NOT the OCR itself)

### Why MT5 for OCR Correction?

```
OCR Process:
  Image → [Tesseract OCR] → Raw Text (may have errors) → [MT5 Correction] → Clean Text

Example:
  Raw OCR:     "paracetamo1 500 rng 2 x daY"  ❌
  MT5 Fixed:   "Paracetamol 500mg, twice daily" ✅
```

**Key Advantages:**
- Fixes common OCR errors (0→O, l→1, rng→mg)
- Multilingual: Works with mixed English/Khmer/French text
- Contextual: Understands medical terminology
- Customizable: Can be fine-tuned on your specific data

---

## How It Works

### 1. Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              OCR Pipeline                       │
├─────────────────────────────────────────────────┤
│ 1. Image Preprocessing                          │
│    └─> Denoise, Enhance, Binarize              │
│                                                 │
│ 2. Tesseract OCR                                │
│    └─> Extract raw text                        │
│                                                 │
│ 3. MT5 AI Correction (ai_corrector.py)         │
│    └─> Fix errors using language model         │
│                                                 │
│ 4. Postprocessing                               │
│    └─> Format, Extract medications             │
└─────────────────────────────────────────────────┘
```

### 2. Prefix-Based Prompting

MT5 uses **task prefixes** to understand what to do:

```python
# Format: "fix_ocr_{language}: {noisy_text}"

Input:  "fix_ocr_eng: paracetamo1 500 rng"
Output: "Paracetamol 500mg"

Input:  "fix_ocr_khm: ថ្នាំ បញ្ចុះ កម្ដៅ"
Output: "ថ្នាំបញ្ចុះកម្ដៅ"

Input:  "fix_ocr_fra: comprimé 2x par jour"
Output: "comprimé 2 fois par jour"
```

### 3. Model Loading Strategy

```python
# Two loading modes:

1. Local Fine-Tuned Model (if exists):
   - Path: ai/mt5/model/
   - Trained on your prescription data
   - Better accuracy for your specific use case

2. Pre-trained from HuggingFace:
   - Name: google/mt5-small
   - General-purpose multilingual model
   - Auto-downloads on first use (~1.2GB)
```

---

## Using the Model

### Basic Usage in Code

```python
from app.ai_corrector import ai_correct

# Single text correction
noisy_text = "paracetamo1 500 rng 2 x daY"
clean_text = ai_correct(noisy_text, lang="eng")
# Result: "Paracetamol 500mg, twice daily"

# With language specification
khmer_text = "ថ្នាំ បញ្ចុះ កម្ដៅ"
corrected = ai_correct(khmer_text, lang="khm")
```

### Batch Processing (More Efficient)

```python
from app.ai_corrector import ai_correct_batch

texts = [
    "paracetamo1 500 rng",
    "amoxici11in 250mg",
    "ibupr0fen 400mg"
]

corrected_texts = ai_correct_batch(texts, lang="eng")
# Processes all at once - faster than loop
```

### Auto-Detection

```python
from app.ai_corrector import detect_and_correct

result = detect_and_correct("asprin l00 mg")
# {
#   "original": "asprin l00 mg",
#   "corrected": "Aspirin 100mg",
#   "detected_language": "english"
# }
```

### Configuration Parameters

```python
ai_correct(
    text="noisy text",
    lang="eng",           # Language: eng, khm, fra
    max_length=128,       # Max output tokens
    num_beams=4           # Beam search width (1-10)
                          # Higher = better quality, slower
)
```

**Performance Trade-offs:**
- `num_beams=1`: Fastest, lower quality (~2s per text)
- `num_beams=4`: Balanced (default) (~5s per text)
- `num_beams=8`: Best quality, slowest (~10s per text)

---

## Customizing the Model

### 1. Adjust Model Behavior

Edit `app/ai_corrector.py`:

```python
def ai_correct(text: str, lang: str = "eng", max_length: int = 128, num_beams: int = 4):
    # Adjust these parameters:
    
    outputs = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        
        max_length=max_length,        # Increase for longer outputs
        num_beams=num_beams,           # Quality vs Speed
        early_stopping=True,           # Stop when confident
        no_repeat_ngram_size=2,        # Avoid repetition
        
        # Advanced options:
        temperature=1.0,               # Randomness (0.1-2.0)
        top_k=50,                      # Top-K sampling
        top_p=0.95,                    # Nucleus sampling
        repetition_penalty=1.2,        # Penalize repetition
    )
```

### 2. Add New Language Support

```python
# In ai_corrector.py, add new language codes:

def ai_correct(text: str, lang: str = "eng", ...):
    """
    Supported languages:
    - eng: English
    - khm: Khmer
    - fra: French
    - spa: Spanish  # NEW
    - deu: German   # NEW
    """
    prompt = f"fix_ocr_{lang}: {text}"
```

Then add training data for the new language.

### 3. Create Domain-Specific Corrections

Add custom post-processing rules:

```python
# In ai_corrector.py, add after correction:

def apply_medical_rules(text: str) -> str:
    """Apply medical prescription-specific rules."""
    replacements = {
        "para": "Paracetamol",
        "amox": "Amoxicillin",
        "ibup": "Ibuprofen",
        "x/day": "times daily",
        "mg/kg": "mg per kg",
    }
    
    for short, full in replacements.items():
        text = text.replace(short, full)
    
    return text

def ai_correct(text: str, lang: str = "eng", ...):
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    corrected = apply_medical_rules(corrected)  # Add this
    return corrected
```

---

## Training Your Own Model

### Step 1: Prepare Training Data

Create a JSON file with input-output pairs:

```json
[
  {
    "lang": "eng",
    "input": "paracetamo1 500 rng 2 x daY",
    "output": "Paracetamol 500mg, twice daily"
  },
  {
    "lang": "khm",
    "input": "ថ្នាំ បញ្ចុះ កម្ដៅ",
    "output": "ថ្នាំបញ្ចុះកម្ដៅ"
  },
  {
    "lang": "fra",
    "input": "comprimé 2x par jour",
    "output": "comprimé 2 fois par jour"
  }
]
```

**Data Collection Tips:**
1. **Collect Real OCR Errors**: Process images → save raw OCR text
2. **Manual Correction**: Have humans correct the OCR errors
3. **Augmentation**: Generate synthetic errors:
   ```python
   # Common OCR errors:
   "O" → "0", "l" → "1", "S" → "5"
   "m" → "rn", "cl" → "d", "vv" → "w"
   ```
4. **Minimum Dataset Size**:
   - Small improvement: 100-500 examples
   - Good results: 1,000-5,000 examples
   - Production quality: 10,000+ examples

### Step 2: Run Training

```bash
cd /home/rayu/DasTern/OCR_System/ocr-backend/ai/fine_tune

# With custom data:
/home/rayu/DasTern/.venv/bin/python train_mt5.py \
    --data_path ./my_training_data.json \
    --output_dir ../mt5 \
    --epochs 3 \
    --batch_size 4 \
    --lr 5e-5

# With sample data (for testing):
/home/rayu/DasTern/.venv/bin/python train_mt5.py
```

**Training Parameters:**
- `--data_path`: Path to your JSON training data
- `--output_dir`: Where to save the trained model (default: `../mt5`)
- `--epochs`: Training iterations (3-10, more epochs = better fit)
- `--batch_size`: Samples per batch (2-8 for CPU, 16-32 for GPU)
- `--lr`: Learning rate (3e-5 to 1e-4, lower = more stable)

**Expected Training Time (CPU):**
- 100 samples: ~10 minutes
- 1,000 samples: ~1-2 hours
- 10,000 samples: ~10-20 hours

**With GPU (if available):**
- Enable in `train_mt5.py`: Change `fp16=False` → `fp16=True`
- 5-10x faster than CPU

### Step 3: Verify Training

After training completes:

```bash
# Check model files exist:
ls -lh ai/mt5/model/
ls -lh ai/mt5/tokenizer/

# Test the trained model:
python3 << EOF
from app.ai_corrector import ai_correct, load_model

# Force reload to use newly trained model
load_model(use_local=True)

# Test correction
result = ai_correct("paracetamo1 500 rng", lang="eng")
print(f"Result: {result}")
EOF
```

### Step 4: Evaluate Performance

Create a test script:

```python
# test_model.py
import json
from app.ai_corrector import ai_correct

# Load test data (separate from training)
with open("test_data.json") as f:
    test_data = json.load(f)

correct = 0
total = len(test_data)

for item in test_data:
    predicted = ai_correct(item["input"], lang=item["lang"])
    expected = item["output"]
    
    if predicted.strip().lower() == expected.strip().lower():
        correct += 1
        print(f"✅ {item['input']} → {predicted}")
    else:
        print(f"❌ {item['input']}")
        print(f"   Expected: {expected}")
        print(f"   Got: {predicted}")

accuracy = (correct / total) * 100
print(f"\nAccuracy: {accuracy:.1f}%")
```

---

## Advanced Usage

### 1. Memory Management

```python
from app.ai_corrector import load_model, unload_model

# Load model once at startup
load_model(use_local=True, device="cpu")

# ... do many corrections ...

# Free memory when done
unload_model()
```

### 2. GPU Acceleration (if available)

```python
import torch

# Check GPU availability
if torch.cuda.is_available():
    device = "cuda"
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = "cpu"

# Load with GPU
load_model(use_local=True, device=device)
```

### 3. Batch Processing for Large Documents

```python
from app.ai_corrector import ai_correct_batch

# Process 100 text blocks efficiently
text_blocks = [...]  # Your 100 blocks

# Split into batches of 10
batch_size = 10
results = []

for i in range(0, len(text_blocks), batch_size):
    batch = text_blocks[i:i+batch_size]
    corrected = ai_correct_batch(batch, lang="eng")
    results.extend(corrected)
```

### 4. Integration with OCR Pipeline

The model is automatically used in the OCR pipeline:

```python
# In app/pipeline.py
from .ai_corrector import ai_correct

def run_pipeline(image_path, use_ai_correction=True, ...):
    # 1. OCR extraction
    raw_text = ocr_engine.extract_text(image)
    
    # 2. AI correction (if enabled)
    if use_ai_correction:
        corrected_text = ai_correct(raw_text, lang=detected_lang)
    else:
        corrected_text = raw_text
    
    return corrected_text
```

### 5. A/B Testing: With vs Without AI Correction

```python
# Test both approaches
result_with_ai = run_pipeline(image, use_ai_correction=True)
result_without_ai = run_pipeline(image, use_ai_correction=False)

print("Without AI:", result_without_ai["full_text"])
print("With AI:", result_with_ai["full_text"])
```

---

## Performance Tuning

### CPU Optimization

```python
# In train_mt5.py or ai_corrector.py
import torch

# Use all CPU cores
torch.set_num_threads(os.cpu_count())

# Optimize for inference
torch.set_grad_enabled(False)
model.eval()
```

### Reduce Model Size (Quantization)

```python
# After training, quantize for faster inference
from transformers import MT5ForConditionalGeneration
import torch

model = MT5ForConditionalGeneration.from_pretrained("ai/mt5/model")

# Apply dynamic quantization
quantized_model = torch.quantization.quantize_dynamic(
    model, 
    {torch.nn.Linear}, 
    dtype=torch.qint8
)

# Save quantized model
quantized_model.save_pretrained("ai/mt5/model_quantized")
```

**Benefits:** 50-70% smaller, 2-3x faster, slight accuracy loss

---

## Troubleshooting

### Issue: Model too slow

**Solutions:**
1. Reduce `num_beams` (4 → 2 → 1)
2. Decrease `max_length` (128 → 64)
3. Use batch processing
4. Enable GPU if available
5. Quantize model

### Issue: Poor correction quality

**Solutions:**
1. Collect more training data (1000+ examples)
2. Increase `num_beams` (4 → 8)
3. Train for more epochs (3 → 5-10)
4. Add domain-specific examples
5. Use data augmentation

### Issue: Out of memory

**Solutions:**
1. Reduce batch size (4 → 2 → 1)
2. Use smaller model (mt5-small is smallest)
3. Process texts one at a time
4. Unload model when not in use
5. Close other applications

### Issue: Model not loading

**Solutions:**
```bash
# Check model files
ls ai/mt5/model/
ls ai/mt5/tokenizer/

# Re-download if missing
cd ai/fine_tune
/home/rayu/DasTern/.venv/bin/python -c "
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
tokenizer = MT5Tokenizer.from_pretrained('google/mt5-small')
model = MT5ForConditionalGeneration.from_pretrained('google/mt5-small')
tokenizer.save_pretrained('../mt5/tokenizer')
model.save_pretrained('../mt5/model')
print('Model downloaded successfully!')
"
```

---

## Summary

### Quick Reference

```python
# 1. Simple correction
from app.ai_corrector import ai_correct
result = ai_correct("paracetamo1 500mg", lang="eng")

# 2. Batch processing
from app.ai_corrector import ai_correct_batch
results = ai_correct_batch(texts, lang="eng")

# 3. Train model
# cd ai/fine_tune
# python train_mt5.py --data_path data.json --epochs 3

# 4. Memory management
from app.ai_corrector import load_model, unload_model
load_model()
# ... use model ...
unload_model()
```

### Key Points to Remember

✅ **MT5 fixes OCR errors** - it doesn't do OCR itself  
✅ **Prefix-based prompting** - "fix_ocr_{lang}: {text}"  
✅ **CPU-friendly** - no GPU required  
✅ **Multilingual** - English, Khmer, French  
✅ **Fine-tunable** - train on your own data  
✅ **Batch processing** - more efficient than loops  

---

For more help, check:
- [HuggingFace MT5 Docs](https://huggingface.co/google/mt5-small)
- [Transformers Library](https://huggingface.co/docs/transformers)
- Training script: `ai/fine_tune/train_mt5.py`
- Corrector module: `app/ai_corrector.py`
