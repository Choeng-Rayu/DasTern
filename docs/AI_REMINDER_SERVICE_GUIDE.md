# AI-LLM Service for OCR-to-Reminder Pipeline

## Overview

This service processes raw OCR data from medical prescriptions and extracts structured medication reminders using LLaMA via Ollama.

**Flow:**
```
Raw OCR JSON → AI Processing (Ollama + LLaMA) → Structured JSON Reminders
```

## Implementation Status

### ✅ Completed

1. **AI Service** (`/home/rayu/DasTern/ai-llm-service`)
   - FastAPI server running on port 8001
   - Ollama integration with llama3.2:3b and llama3.1:8b models
   - `/extract-reminders` endpoint for medication extraction
   - Simplified, optimized prompts for Khmer/English/French prescriptions

2. **OCR Service** (`/home/rayu/DasTern/ocr-service`)
   - Already installed and configured
   - Extracts text from prescription images
   - Provides raw OCR JSON output

3. **Optimized Prompts** (`app/prompts/reminder_prompts.py`)
   - Concise system prompt with explicit Khmer→English translations
   - Clear JSON format specification
   - Example-based few-shot learning
   - Optimized for fast inference

4. **Reminder Engine** (`app/features/reminder_engine.py`)
   - Extracts medications with timing information
   - Validates JSON structure and time formats
   - Maps times to 24-hour format (08:00, 12:00, 18:00, 21:00)
   - Handles retries and error cases

5. **JSON Schema** (`app/schemas.py`)
   - Strict validation for medication reminders
   - Canonical format for reminder engine

### ⚠️ Current Limitation

**Hardware Constraint:** Ollama is running on CPU only, causing response times of 40-120+ seconds. For production use, GPU acceleration is recommended.

## API Endpoints

### Health Check
```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ollama-ai-service",
  "ollama_connected": true
}
```

### Extract Reminders
```bash
curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{
    "raw_ocr_json": {
      "text": "Butylscopolami 5 viên | ល្ងាច | យប់"
    }
  }'
```

**Expected Response:**
```json
{
  "medications": [
    {
      "name": "Butylscopolamine",
      "times": ["evening", "night"],
      "times_24h": ["18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "ល្ងាច | យប់"
    }
  ],
  "success": true,
  "error": null,
  "metadata": {
    "model": "llama3.2:3b",
    "attempts": 1
  }
}
```

## Canonical JSON Format

The AI service returns medication reminders in this strict format:

```json
{
  "medications": [
    {
      "name": "string (required)",
      "times": ["morning", "noon", "evening", "night"],
      "times_24h": ["08:00", "12:00", "18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null | integer,
      "notes": "string"
    }
  ]
}
```

### Field Descriptions

- **name**: Medication name (OCR errors corrected, e.g., "Butylscopolami" → "Butylscopolamine")
- **times**: Array of time periods in English (morning, noon, evening, night)
- **times_24h**: Corresponding 24-hour times (08:00, 12:00, 18:00, 21:00)
- **repeat**: Frequency (always "daily" for now)
- **duration_days**: Number of days (null if not specified in prescription)
- **notes**: Original Khmer text or additional context

### Time Mapping Table

| Khmer | French | English | 24h Time |
|-------|--------|---------|----------|
| ព្រឹក | matin | morning | 08:00 |
| ថ្ងៃ | midi | noon | 12:00 |
| ល្ងាច | soir | evening | 18:00 |
| យប់ | nuit | night | 21:00 |

## Testing

### Quick Test Script
```bash
cd /home/rayu/DasTern/OCR_Test_Space
python3 test_ollama_simple.py
```

### Full Pipeline Test
```bash
cd /home/rayu/DasTern/OCR_Test_Space
python3 test_full_pipeline.py
```

## Configuration

### Environment Variables
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b  # or llama3.1:8b for better accuracy
```

### Starting the Service
```bash
cd /home/rayu/DasTern/ai-llm-service
python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001 --reload
```

## Prompt Optimization

The prompts have been optimized for:
1. **Speed**: Concise instructions reduce token count
2. **Accuracy**: Explicit Khmer→English translations
3. **Consistency**: Clear JSON format with examples
4. **Reliability**: Single prompt approach (no system/user separation)

### Key Prompt Elements

**System Prompt:**
- Explicit translation table (Khmer/French → English)
- Clear rules about time extraction
- Common OCR error corrections
- Output format specification

**User Prompt:**
- Raw OCR data embedded
- JSON format template
- Working example with input/output
- Critical rules reminder

## Production Recommendations

1. **Add GPU Support**: Ollama performs significantly better with GPU acceleration
2. **Implement Caching**: Cache common extraction patterns
3. **Add Fallback**: Use rule-based extraction for simple cases
4. **Monitor Performance**: Track response times and accuracy
5. **Model Selection**: Use llama3.1:8b for accuracy, llama3.2:3b for speed

## Example Prescription Processing

### Input (Raw OCR)
```json
{
  "text": "Butylscopolamine 10mg | ព្រឹក 1 | ល្ងាច 1 | យប់ 1"
}
```

### Output (AI Processed)
```json
{
  "medications": [
    {
      "name": "Butylscopolamine 10mg",
      "times": ["morning", "evening", "night"],
      "times_24h": ["08:00", "18:00", "21:00"],
      "repeat": "daily",
      "duration_days": null,
      "notes": "ព្រឹក 1 | ល្ងាច 1 | យប់ 1"
    }
  ]
}
```

## Files Modified

1. `/home/rayu/DasTern/ai-llm-service/app/prompts/reminder_prompts.py` - Simplified prompts
2. `/home/rayu/DasTern/ai-llm-service/app/features/reminder_engine.py` - Validation fixes
3. `/home/rayu/DasTern/OCR_Test_Space/test_ollama_simple.py` - Working test script

## Next Steps for Your Teammate

The reminder engine interface can now:
1. Send raw OCR JSON to `http://localhost:8001/extract-reminders`
2. Receive structured medication reminders
3. Use the reminders directly without modification
4. Handle the canonical JSON format consistently

The AI service is ready for integration with the reminder engine interface!
