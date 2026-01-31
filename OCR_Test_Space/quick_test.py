#!/usr/bin/env python3
"""
Quick test of enhanced OCR on a single image
"""
import sys
import json
import cv2
from pathlib import Path

# Add ocr-service to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ocr-service"))

from app.ocr.extractors.medical_ocr import extract_medical_prescription

# Test with first prescription image
image_path = Path(__file__).parent / "images" / "image1.png"

print(f"Loading: {image_path}")
image = cv2.imread(str(image_path))

print("Running enhanced OCR...")
result = extract_medical_prescription(
    image,
    apply_advanced_preprocessing=True,
    detect_tables=True,
    extract_structured=True,
    upscale_factor=1.5
)

# Save result
output_path = Path(__file__).parent / "results" / "quick_test_result.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nSaved to: {output_path}")
print(f"\nTotal OCR elements: {len(result['raw'])}")
print(f"Average confidence: {result['stats']['avg_confidence']:.1f}%")
print(f"Table detected: {result['table_detection']['found']}")

if result['structured_data']:
    meds = result['structured_data'].get('medications', [])
    table_meds = result['structured_data'].get('table_medications', [])
    print(f"Medications found: {len(meds)}")
    print(f"Table medications: {len(table_meds)}")
    
    if table_meds:
        print("\nMedications from table:")
        for idx, med in enumerate(table_meds[:5], 1):
            print(f"  {idx}. {med['name']} - {med.get('dosage', 'N/A')}")

print("\nDone!")
