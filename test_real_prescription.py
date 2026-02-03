#!/usr/bin/env python3
"""Test AI enhancement with real OCR data"""

import requests
import json

# The raw OCR JSON from your prescription
ocr_data = {
  "meta": {
    "languages": ["eng", "khm", "fra"],
    "dpi": 71,
    "processing_time_ms": 1967.9522514343262,
    "model_version": "default"
  },
  "quality": {
    "blur": "low",
    "blur_score": 1802.9228543629022,
    "contrast": "ok",
    "contrast_score": 44.68520600625875,
    "skew_angle": -2.0825652797308845,
    "dpi": 71,
    "is_grayscale": False
  },
  "blocks": [
    {
      "type": "text",
      "bbox": {"x": 0, "y": 0, "width": 975, "height": 1312},
      "lines": [
        {"text": "DCE H. យ វ EP |", "confidence": 0.58, "language": "en"},
        {"text": "KhmerSovet កករ Horn", "confidence": 0.22, "language": "en"},
        {"text": "លេខកូដ: HAKF1354164 ឈ្មោះអ្នកជំងឺ: ង៉ាំ ដានី អាយុ: 19 ឆ្នាំ ភេទ: ស្រី |", "confidence": 0.92, "language": "kh"},
        {"text": "ប្រភេទបង់ប្រាក់ : មូលនិធិសមធម៌ / 20051002-0409 |", "confidence": 0.81, "language": "kh"},
        {"text": "រោគវិនិច្ឆ័យ : 1. Chronic Cystitis", "confidence": 0.94, "language": "en"},
        {"text": "2. Encour ménorhée", "confidence": 0.93, "language": "fr"},
        {"text": "ផ្នែក : ពិគ្រោះជំងឺក្រៅ - បន្ទប់លេខ 5 :", "confidence": 0.85, "language": "kh"},
        {"text": "វេជ្ជបញ្ជា ស", "confidence": 0.66, "language": "kh"},
        {"text": "Esome 20mg |7 គ្រាប់ស្រោប| PO |គ្រាប់ ក្រោយបាយ ន", "confidence": 0.75, "language": "kh", "tags": ["time_candidate", "quantity_candidate"]},
        {"text": "រាជធានីភ្នំពេញ,ថ្ងៃទី 22/06/2", "confidence": 0.60, "language": "kh", "tags": ["time_candidate"]}
      ],
      "raw_text": "DCE H. យ វ EP |\nKhmerSovet កករ Horn\nលេខកូដ: HAKF1354164 ឈ្មោះអ្នកជំងឺ: ង៉ាំ ដានី អាយុ: 19 ឆ្នាំ ភេទ: ស្រី |\nប្រភេទបង់ប្រាក់ : មូលនិធិសមធម៌ / 20051002-0409 |\nរោគវិនិច្ឆ័យ : 1. Chronic Cystitis\n2. Encour ménorhée\nផ្នែក : ពិគ្រោះជំងឺក្រៅ - បន្ទប់លេខ 5 :\nវេជ្ជបញ្ជា ស\nEsome 20mg |7 គ្រាប់ស្រោប| PO |គ្រាប់ ក្រោយបាយ ន\nរាជធានីភ្នំពេញ,ថ្ងៃទី 22/06/2"
    }
  ],
  "full_text": "",
  "success": False,
  "error": None
}

print("=" * 70)
print("🧪 Testing AI Enhancement with Real Prescription")
print("=" * 70)
print("\n📋 Prescription Info:")
print("   - Languages: Khmer, English, French")
print("   - Diagnosis: Chronic Cystitis")
print("   - Visible medication: Esome 20mg")
print("\n⏳ Sending to AI service...")
print("   (This will take 20-90 seconds, please wait...)\n")

try:
    import time
    start_time = time.time()
    
    response = requests.post(
        "http://localhost:8001/extract-reminders",
        json={"raw_ocr_json": ocr_data},
        timeout=120  # 2 minutes max
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ AI Enhancement SUCCESS in {elapsed:.1f} seconds")
        print("\n" + "=" * 70)
        print("📊 RESULTS:")
        print("=" * 70)
        
        if result.get('success'):
            medications = result.get('medications', [])
            print(f"\n✅ Success: {result.get('success')}")
            print(f"📦 Medications extracted: {len(medications)}\n")
            
            if medications:
                for i, med in enumerate(medications, 1):
                    print(f"{'─' * 70}")
                    print(f"Medication #{i}:")
                    print(f"{'─' * 70}")
                    print(f"  Name:         {med.get('name', 'N/A')}")
                    print(f"  Dosage:       {med.get('dosage', 'N/A')}")
                    print(f"  Times:        {', '.join(med.get('times', []))}")
                    print(f"  Times (24h):  {', '.join(med.get('times_24h', []))}")
                    print(f"  Repeat:       {med.get('repeat', 'N/A')}")
                    print(f"  Duration:     {med.get('duration_days', 'N/A')} days")
                    print(f"  Notes:        {med.get('notes', 'N/A')}")
                    print()
                
                print("=" * 70)
                print("✅ AI ENHANCEMENT IS WORKING!")
                print("=" * 70)
            else:
                print("⚠️  No medications extracted (AI may need better prompts)")
        else:
            print(f"❌ Success: {result.get('success')}")
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ TIMEOUT - Request took longer than 2 minutes")
    print("   The AI service may need longer timeout (currently 600s)")
    print("   Or the model is too slow for this prescription")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
