#!/usr/bin/env python3
"""
View OCR Test Results
Displays a summary of all test results
"""
import json
from pathlib import Path

results_dir = Path(__file__).parent / "results"

# Find all result files
result_files = sorted(results_dir.glob("result_*.json"), 
                     key=lambda f: int(f.stem.split('_')[1]))

if not result_files:
    print("No result files found!")
    exit(1)

print("=" * 80)
print("OCR TEST RESULTS SUMMARY")
print("=" * 80)
print(f"Found {len(result_files)} result file(s)\n")

for result_file in result_files:
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result_num = data.get('result_number', '?')
    image_name = data.get('image_name', 'unknown')
    processing_time = data.get('processing_time_seconds', 0)
    
    ocr_results = data.get('ocr_results', {})
    stats = ocr_results.get('stats', {})
    table_info = ocr_results.get('table_detection', {})
    structured = ocr_results.get('structured_data', {})
    
    print(f"\n{'─' * 80}")
    print(f"Result #{result_num}: {image_name}")
    print(f"{'─' * 80}")
    print(f"Processing Time: {processing_time:.2f}s")
    print(f"Total Words: {stats.get('total_words', 0)}")
    print(f"Avg Confidence: {stats.get('avg_confidence', 0):.1f}%")
    
    if table_info.get('found'):
        table_data = table_info.get('data', {})
        print(f"Table: {table_data.get('rows', 0)}x{table_data.get('columns', 0)}")
    
    if structured:
        meds = structured.get('medications', [])
        table_meds = structured.get('table_medications', [])
        total_meds = len(meds) + len(table_meds)
        
        patient = structured.get('patient', {})
        if patient.get('name') or patient.get('id'):
            print(f"Patient: {patient.get('name') or patient.get('id') or 'N/A'}")
        
        if total_meds > 0:
            print(f"Medications Found: {total_meds}")
            
            # Show first few medications
            all_meds = meds + table_meds
            for idx, med in enumerate(all_meds[:3], 1):
                print(f"  {idx}. {med['name']}", end='')
                if med.get('dosage'):
                    print(f" - {med['dosage']}", end='')
                if med.get('frequency'):
                    print(f" - {med['frequency']}", end='')
                print()
            
            if total_meds > 3:
                print(f"  ... and {total_meds - 3} more")
        
        dates = structured.get('dates', [])
        if dates:
            print(f"Dates: {len(dates)} found")

print("\n" + "=" * 80)
print("Results files location:", results_dir)
print("=" * 80)
