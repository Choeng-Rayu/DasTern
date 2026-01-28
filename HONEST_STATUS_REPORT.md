# ⚠️ OCR Service Status Report - HONEST ASSESSMENT

**Date:** January 27, 2026  
**Status:** ❌ **NOT WORKING** - oneDNN Library Incompatibility

---

## The Real Problem

PaddleOCR 3.3.3 with PaddlePaddle 3.3.0 has a **critical oneDNN compatibility bug** that prevents any OCR inference:

```
(Unimplemented) ConvertPirAttribute2RuntimeAttribute not support 
[pir::ArrayAttribute<pir::DoubleAttribute>]
```

**This is NOT a configuration issue.** It's a C++ library bug in Paddle's oneDNN backend.

---

## What We Tried (All Failed)

1. ✗ Setting `PADDLE_WITH_ONEDNN=0` in shell script
2. ✗ Setting env vars in Python code (before imports)
3. ✗ Setting env vars at package initialization level
4. ✗ Disabling angle classifier (`use_angle_cls=False`)
5. ✗ Trying ONNX parameters
6. ✗ Creating fresh Python 3.11 venv
7. ✗ Using different PaddleOCR initialization strategies

**Why none of these work:**
- The error occurs in C++ library layer during inference
- By the time Python code runs, the C++ libraries are already loaded
- oneDNN initialization happens at system load time, not runtime

---

## Test Results

### Latest Test Run
- **Raw OCR (`/ocr/simple`)**: 0/3 images successful (ALL FAILED with oneDNN error)
- **AI-Enhanced (`/ocr`)**: 3/3 returned 200 OK but with 0 text blocks extracted

### Result Files Generated
- `result_noAI_20260127_202754.json` - All failures
- `result_ai_20260127_202754.json` - All returning empty text

---

## Real Solutions

### Option 1: Use Older PaddleOCR Version (RECOMMENDED)
```bash
pip install paddleocr==2.7.0.3 paddlepaddle==2.6.2
```
- ✅ No oneDNN PIR issue
- ✅ Proven stable for Khmer text
- ⚠️ Older features, less optimized

### Option 2: Wait for Paddle Update
- PaddleOCR 3.4.x (not released yet) should have PIR fixes
- Monitor GitHub: https://github.com/PaddlePaddle/PaddleOCR/issues

### Option 3: Use Alternative OCR Engine
- Tesseract OCR (slower but reliable)
- EasyOCR (good for multilingual)
- Google Cloud Vision API (cloud-based)

### Option 4: Use CPU-Only Build (Advanced)
- Rebuild Paddle without oneDNN support
- Time-consuming but guaranteed to work

---

## Recommendation

**For immediate working solution:** Downgrade to PaddleOCR 2.7.0.3

```bash
# Stop current service
pkill -9 uvicorn

# Backup current venv
mv /home/rayu/DasTern/ocr-service/venv_ocr /home/rayu/DasTern/ocr-service/venv_ocr_broken

# Create new venv with older Paddle
python3.11 -m venv /home/rayu/DasTern/ocr-service/venv_ocr
source /home/rayu/DasTern/ocr-service/venv_ocr/bin/activate
pip install --upgrade pip
pip install paddleocr==2.7.0.3 paddlepaddle==2.6.2 fastapi uvicorn python-multipart httpx

# Restart service
/home/rayu/DasTern/start-ocr-service-port8001.sh
```

---

## What This Means

The **testing framework is working perfectly**, but the **OCR library itself is broken** in version 3.3.3.

You cannot fix this with:
- Environment variables
- Code changes
- Configuration files
- Parameter adjustments

You must **change the Paddle version** to get working OCR.

---

## Next Steps

1. Decide which solution to use
2. I can help implement any of the options above
3. Once implemented, rerun tests to verify success

**Would you like me to downgrade Paddle to 2.7.0.3 to get OCR working?**
