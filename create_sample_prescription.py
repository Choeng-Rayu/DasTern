#!/usr/bin/env python3
"""
Create a sample prescription from OCR data with fallback medications
This allows testing Flutter UI while waiting for AI service
"""
import json
import time
from datetime import datetime
import os

OCR_DATA = {
  "meta": {
    "languages": ["eng", "khm", "fra"],
    "dpi": 71,
    "processing_time_ms": 2297.294855117798
  },
  "quality": {
    "blur": "low",
    "contrast": "ok"
  },
  "blocks": [
    {
      "raw_text": "LPS 2 | SOK HENG POLYCLINIC\nฟPrescription\nPatient: Age ~35\nDiagnosis: Asthénie\n- TA:100/65 mmHg\n- P:90 /min\n- T°: 36,7°C"
    }
  ]
}

def create_sample_prescription():
    """Create a sample prescription with extracted medications"""
    
    data_folder = "/home/rayu/DasTern/ocr_ai_for_reminder/data"
    os.makedirs(data_folder, exist_ok=True)
    
    timestamp_ms = int(time.time() * 1000)
    prescription_id = str(timestamp_ms)
    
    # Sample medications extracted from prescription
    medications = [
        {
            "name": "Paracetamol",
            "dosage": "500mg",
            "times": ["08:00", "14:00", "20:00"],
            "times24h": [8, 14, 20],
            "repeat": "daily",
            "durationDays": 7,
            "notes": "Take with food"
        },
        {
            "name": "Amoxicillin",
            "dosage": "500mg",
            "times": ["08:00", "20:00"],
            "times24h": [8, 20],
            "repeat": "daily",
            "durationDays": 7,
            "notes": "Antibiotic for infection"
        },
        {
            "name": "Vitamin B Complex",
            "dosage": "1 tablet",
            "times": ["08:00"],
            "times24h": [8],
            "repeat": "daily",
            "durationDays": 14,
            "notes": "For energy and fatigue"
        }
    ]
    
    prescription_data = {
        "id": prescription_id,
        "createdAt": datetime.now().isoformat(),
        "medications": medications,
        "patientName": "SOK HENG",
        "age": 35,
        "diagnosis": "Asthénie (Fatigue)",
        "rawOcrData": OCR_DATA,
        "aiMetadata": {
            "model": "llama3.2:3b",
            "processingTime": 2500,
            "confidence": 0.85
        }
    }
    
    prescriptions_file = f"{data_folder}/prescriptions.json"
    
    if os.path.exists(prescriptions_file):
        with open(prescriptions_file, 'r') as f:
            prescriptions_list = json.load(f)
    else:
        prescriptions_list = []
    
    prescriptions_list.append(prescription_data)
    
    with open(prescriptions_file, 'w') as f:
        json.dump(prescriptions_list, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print("✅ Sample Prescription Created Successfully")
    print("=" * 70)
    print()
    print(f"📁 Saved to: {prescriptions_file}")
    print(f"📋 Prescription ID: {prescription_id}")
    print(f"👤 Patient: {prescription_data['patientName']}")
    print(f"🏥 Diagnosis: {prescription_data['diagnosis']}")
    print(f"💊 Medications: {len(medications)}")
    print()
    print("Medications:")
    for i, med in enumerate(medications, 1):
        times_str = ", ".join(med['times'])
        print(f"  {i}. {med['name']} - {med['dosage']}")
        print(f"     Times: {times_str} | Duration: {med['durationDays']} days")
    print()
    print("=" * 70)
    print("Next Steps:")
    print("1. Run Flutter: cd /home/rayu/DasTern/ocr_ai_for_reminder && flutter run -d linux")
    print("2. Click 'View Saved Prescriptions' on home screen")
    print("3. You'll see the prescription loaded and displayed")
    print("=" * 70)

if __name__ == "__main__":
    create_sample_prescription()
