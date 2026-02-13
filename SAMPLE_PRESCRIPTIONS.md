# Sample Prescription Texts for Demo

Use these if you don't have a real prescription image handy.

## Sample 1: Simple Single Medication
```
Paracetamol 500mg
Take 2 tablets 3 times daily after meals
Duration: 5 days
```

## Sample 2: Multiple Medications
```
PRESCRIPTION

1. Amoxicillin 500mg
   Take 1 capsule 3 times daily with food
   Duration: 7 days

2. Paracetamol 500mg
   Take 2 tablets when needed for pain
   Maximum 4 times per day

3. Omeprazole 20mg
   Take 1 tablet once daily before breakfast
   Duration: 14 days
```

## Sample 3: With OCR Errors (for correction demo)
```
Paracetam0l 50Omg
Take 2 tab1ets 3 t1mes dai1y
Amox1cillin 500mg
Take 1 capsu1e 3 times dai1y
```

## Sample 4: Complex Schedule
```
Metformin 500mg
Take 1 tablet twice daily with meals (breakfast and dinner)
Duration: 30 days

Aspirin 75mg
Take 1 tablet once daily in the morning
Long-term medication

Atorvastatin 10mg
Take 1 tablet once daily at bedtime
Duration: 30 days
```

## Sample 5: Multilingual (English + French)
```
ORDONNANCE / PRESCRIPTION

Amoxicilline 500mg
Prendre 1 gélule 3 fois par jour
Duration: 7 jours

Paracétamol 500mg
Take 2 tablets 3 times daily
Durée: 5 days
```

---

## Quick Test Commands

### Test OCR Correction with Sample 3:
```bash
curl -X POST http://127.0.0.1:8001/correct-ocr \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Paracetam0l 50Omg\nTake 2 tab1ets 3 t1mes dai1y\nAmox1cillin 500mg\nTake 1 capsu1e 3 times dai1y",
    "language": "en"
  }' | jq
```

### Test Reminder Extraction with Sample 2:
```bash
curl -X POST http://127.0.0.1:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{
    "raw_ocr_json": {
      "full_text": "Amoxicillin 500mg\nTake 1 capsule 3 times daily with food\nDuration: 7 days\n\nParacetamol 500mg\nTake 2 tablets when needed for pain\nMaximum 4 times per day\n\nOmeprazole 20mg\nTake 1 tablet once daily before breakfast\nDuration: 14 days"
    }
  }' | jq
```

### Test with Sample 4 (Complex):
```bash
curl -X POST http://127.0.0.1:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d '{
    "raw_ocr_json": {
      "full_text": "Metformin 500mg\nTake 1 tablet twice daily with meals (breakfast and dinner)\nDuration: 30 days\n\nAspirin 75mg\nTake 1 tablet once daily in the morning\nLong-term medication\n\nAtorvastatin 10mg\nTake 1 tablet once daily at bedtime\nDuration: 30 days"
    }
  }' | jq
```

---

## Creating Test Images

If you need to create prescription images for testing:

### Option 1: Screenshot
1. Open a text editor
2. Type one of the samples above in large font (18-24pt)
3. Take a screenshot
4. Save as JPG/PNG

### Option 2: Use an existing image
```bash
# Find sample prescription images online or use:
# /Users/macbook/Pictures/screenshot/2026-02-11 09.44.24.jpg
```

### Option 3: Create with ImageMagick (if installed)
```bash
convert -size 800x600 -background white -fill black \
  -font Arial -pointsize 24 \
  -gravity center \
  label:"Paracetamol 500mg\nTake 2 tablets\n3 times daily" \
  prescription_sample.jpg
```

---

## Pro Tips for Demo

1. **Start with Sample 1** - Simple and guaranteed to work
2. **Show Sample 3** for OCR correction - Very impressive!
3. **Use Sample 2** for reminder extraction - Shows multiple meds
4. **Save Sample 4** for "wow factor" - Complex schedules

**Keep these samples open in a text editor during demo for quick copy-paste!**
