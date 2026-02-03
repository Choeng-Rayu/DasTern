#!/usr/bin/env python3
"""Debug script to test fast parser locally"""

import sys
sys.path.insert(0, '/home/rayu/DasTern/ai-llm-service')

from app.features.prescription.fast_parser import FastPrescriptionParser
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

sample_prescription = """
Patient: SENG Sophal
Age: 45 years
Date: 2025-01-28

Medications:
1. Paracetamol 500mg - Take 2 times daily (morning and evening)
2. Amoxicillin 250mg - Take 3 times daily for 7 days
3. Omeprazole 20mg - Take once daily before breakfast

Doctor: Dr. Chhay Meng
Clinic: Phnom Penh Medical Center
"""

parser = FastPrescriptionParser()

# Test line by line parsing
print("🔍 Testing individual lines:\n")
lines = sample_prescription.split('\n')
for i, line in enumerate(lines, 1):
    if 'Paracetamol' in line or 'Amoxicillin' in line or 'Omeprazole' in line:
        print(f"Line {i}: {line}")
        med = parser._parse_medication_line(line)
        if med:
            print(f"  ✅ Parsed: {med['name']} - {med['dosage']}")
        else:
            print(f"  ❌ NOT PARSED")
        print()

print("\n" + "=" * 60)
print("Full parse result:")
print("=" * 60)

result = parser.parse(sample_prescription)

print(f"\n📊 Results:")
print(f"Patient: {result['patient_info']['name']} (age {result['patient_info']['age']})")
print(f"Medications found: {len(result['medications'])}")

for i, med in enumerate(result['medications'], 1):
    print(f"\n  {i}. {med['name']}")
    print(f"     Dosage: {med['dosage']}")
    print(f"     Frequency: {med['frequency']}")

