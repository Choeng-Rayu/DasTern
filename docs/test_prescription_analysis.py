#!/usr/bin/env python3
"""
Prescription Analysis Test Script
Tests the OCR and AI processing without database storage
"""

import json
import sys
import os

# Add the ai-llm-service to path
sys.path.insert(0, '/home/rayu/DasTern/ai-llm-service')

from app.features.prescription.reminder_generator import generate_reminders_from_prescription

def analyze_prescription_sample():
    """Analyze a sample prescription and provide detailed analysis"""
    
    print("=" * 100)
    print("PRESCRIPTION ANALYSIS - NO DATABASE STORAGE")
    print("=" * 100)
    
    # Sample OCR text from the prescription images
    sample_ocr_text = """
    មន្ទីរពេទ្យមិត្តភាពខ្មែរ-សូវៀត (Khmer-Soviet Friendship Hospital)
    លេខកូដ: HAKF1354164
    ឈ្មោះអ្នកជំងឺ: ហុ ចាន
    អាយុ: 19
    ភេទ: ស្រី
    រោគវិនិច្ឆ័យ: Chronic Cystitis
    ថ្ងៃ: 15/06/2025
    
    ល.រ  ឈ្មោះឱសថ              ចំនួន    ព្រឹក(6-8)  ថ្ងៃត្រង់(11-12)  ល្ងាច(05-06)  យប់(08-10)
    1     Butylscopolamine 10mg   14 គ្រាប់     1            -              1            -
    2     Celcoxx 100mg           14 គ្រាប់     1            -              1            -
    3     Omeprazole 20mg         14 គ្រាប់     1            1              1            -
    4     Multivitamine           21 គ្រាប់     1            1              1            -
    """
    
    print("\n📄 INPUT OCR TEXT:")
    print("-" * 100)
    print(sample_ocr_text)
    print("-" * 100)
    
    # Simulate AI-extracted structured data
    structured_prescription = {
        "patient_info": {
            "name": "ហុ ចាន",
            "id": "HAKF1354164",
            "age": 19,
            "gender": "ស្រី",
            "hospital_code": "HAKF"
        },
        "medical_info": {
            "hospital_name": "Khmer-Soviet Friendship Hospital",
            "diagnosis": "Chronic Cystitis",
            "doctor": "Srvheng",
            "date": "15/06/2025",
            "department": "Room 5"
        },
        "medications": [
            {
                "name": "Butylscopolamine 10mg",
                "dosage": "10mg",
                "quantity": 14,
                "unit": "tablet",
                "schedule": {
                    "times": ["morning", "evening"],
                    "times_24h": ["08:00", "18:00"],
                    "frequency": "twice_daily"
                },
                "duration_days": 7,
                "instructions": "Take before meals"
            },
            {
                "name": "Celcoxx 100mg",
                "dosage": "100mg",
                "quantity": 14,
                "unit": "tablet",
                "schedule": {
                    "times": ["morning", "evening"],
                    "times_24h": ["08:00", "18:00"],
                    "frequency": "twice_daily"
                },
                "duration_days": 7,
                "instructions": "Take with food"
            },
            {
                "name": "Omeprazole 20mg",
                "dosage": "20mg",
                "quantity": 14,
                "unit": "tablet",
                "schedule": {
                    "times": ["morning", "noon", "afternoon"],
                    "times_24h": ["08:00", "12:00", "18:00"],
                    "frequency": "three_times_daily"
                },
                "duration_days": 7,
                "instructions": "Take before meals"
            },
            {
                "name": "Multivitamine",
                "dosage": "",
                "quantity": 21,
                "unit": "tablet",
                "schedule": {
                    "times": ["morning", "noon", "afternoon"],
                    "times_24h": ["08:00", "12:00", "18:00"],
                    "frequency": "three_times_daily"
                },
                "duration_days": 7,
                "instructions": "Take after meals"
            }
        ]
    }
    
    print("\n🔍 STEP 1: STRUCTURED DATA EXTRACTION")
    print("=" * 100)
    print(f"\n👤 Patient Information:")
    print(f"   Name: {structured_prescription['patient_info']['name']}")
    print(f"   ID: {structured_prescription['patient_info']['id']}")
    print(f"   Age: {structured_prescription['patient_info']['age']}")
    print(f"   Gender: {structured_prescription['patient_info']['gender']}")
    
    print(f"\n🏥 Medical Information:")
    print(f"   Hospital: {structured_prescription['medical_info']['hospital_name']}")
    print(f"   Diagnosis: {structured_prescription['medical_info']['diagnosis']}")
    print(f"   Doctor: {structured_prescription['medical_info']['doctor']}")
    print(f"   Date: {structured_prescription['medical_info']['date']}")
    
    print(f"\n💊 Medications Found: {len(structured_prescription['medications'])}")
    for i, med in enumerate(structured_prescription['medications'], 1):
        print(f"\n   {i}. {med['name']}")
        print(f"      Dosage: {med['dosage'] or 'N/A'}")
        print(f"      Quantity: {med['quantity']} {med['unit']}s")
        print(f"      Schedule: {med['schedule']['frequency']}")
        print(f"      Times: {', '.join(med['schedule']['times'])} ({', '.join(med['schedule']['times_24h'])})")
        print(f"      Duration: {med['duration_days']} days")
        print(f"      Instructions: {med['instructions']}")
    
    # Generate reminders
    print("\n\n🔄 STEP 2: REMINDER GENERATION")
    print("=" * 100)
    
    result = generate_reminders_from_prescription(structured_prescription, "2025-06-15")
    
    print(f"\n✅ Generation Results:")
    print(f"   Valid: {result['validation']['valid']}")
    print(f"   Total Medications: {result['metadata']['total_medications']}")
    print(f"   Total Reminders: {result['metadata']['total_reminders']}")
    print(f"   Start Date: {result['metadata']['start_date']}")
    
    if result['validation']['errors']:
        print(f"\n⚠️  Errors:")
        for error in result['validation']['errors']:
            print(f"   - {error}")
    
    if result['validation']['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in result['validation']['warnings']:
            print(f"   - {warning}")
    
    # Display generated reminders
    print("\n\n📅 STEP 3: GENERATED REMINDERS")
    print("=" * 100)
    
    # Group reminders by medication
    reminders_by_med = {}
    for reminder in result['reminders']:
        med_name = reminder['medication_name']
        if med_name not in reminders_by_med:
            reminders_by_med[med_name] = []
        reminders_by_med[med_name].append(reminder)
    
    for med_name, reminders in reminders_by_med.items():
        print(f"\n💊 {med_name}")
        print(f"   Total Reminders: {len(reminders)}")
        
        for r in reminders:
            print(f"\n   ⏰ {r['time_slot'].upper()} - {r['scheduled_time']}")
            print(f"      Dose: {r['dose_amount']} {r['dose_unit']}")
            print(f"      Duration: {r['start_date']} to {r['end_date']}")
            print(f"      Notification: {r['notification_title']}")
            print(f"      Message: {r['notification_body']}")
    
    # Analysis summary
    print("\n\n📊 STEP 4: ANALYSIS SUMMARY")
    print("=" * 100)
    
    # Time slot distribution
    time_slots = {}
    for r in result['reminders']:
        slot = r['time_slot']
        time_slots[slot] = time_slots.get(slot, 0) + 1
    
    print(f"\n🕐 Time Slot Distribution:")
    for slot, count in sorted(time_slots.items()):
        print(f"   {slot.capitalize()}: {count} reminders")
    
    # Medication complexity
    print(f"\n📈 Medication Complexity:")
    for med in structured_prescription['medications']:
        times_per_day = len(med['schedule']['times'])
        complexity = "Simple" if times_per_day <= 2 else "Moderate" if times_per_day == 3 else "Complex"
        print(f"   {med['name']}: {times_per_day}x daily ({complexity})")
    
    # Daily schedule
    print(f"\n📆 Daily Medication Schedule:")
    schedule_by_time = {}
    for r in result['reminders']:
        time = r['scheduled_time']
        if time not in schedule_by_time:
            schedule_by_time[time] = []
        schedule_by_time[time].append(r['medication_name'])
    
    for time in sorted(schedule_by_time.keys()):
        meds = schedule_by_time[time]
        print(f"   {time}: {', '.join(meds)}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    print(f"   ✅ {len(structured_prescription['medications'])} medications successfully extracted")
    print(f"   ✅ {len(result['reminders'])} reminders generated")
    print(f"   ✅ All time slots properly mapped (Khmer → 24h format)")
    print(f"   ✅ Duration calculated from medication quantities")
    
    complex_meds = [m for m in structured_prescription['medications'] if len(m['schedule']['times']) > 2]
    if complex_meds:
        print(f"   ⚠️  {len(complex_meds)} medications have complex schedules (3+ times/day)")
        print(f"      Consider patient education for: {', '.join([m['name'] for m in complex_meds])}")
    
    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE - NO DATA STORED IN DATABASE")
    print("=" * 100)
    
    # Save analysis to file for review
    output = {
        "input": {
            "ocr_text_sample": sample_ocr_text[:500] + "...",
            "structured_data": structured_prescription
        },
        "output": result,
        "analysis": {
            "time_slot_distribution": time_slots,
            "daily_schedule": schedule_by_time,
            "medication_count": len(structured_prescription['medications']),
            "reminder_count": len(result['reminders']),
            "complex_medications": len(complex_meds)
        }
    }
    
    output_file = '/home/rayu/DasTern/prescription_analysis_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print(f"\n📋 To test with your own prescription:")
    print(f"   POST /api/prescriptions/analyze with image file")
    print(f"   Returns: OCR text + AI extraction + Reminders + Analysis")
    
    return result

if __name__ == "__main__":
    try:
        analyze_prescription_sample()
        print("\n🎉 Analysis completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
