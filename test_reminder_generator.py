#!/usr/bin/env python3
"""
Test script for Prescription to Reminder conversion
Tests the AI service reminder generation functionality
"""

import json
import sys
import os

# Add the ai-llm-service to path
sys.path.insert(0, '/home/rayu/DasTern/ai-llm-service')

from app.features.prescription.reminder_generator import ReminderGenerator, generate_reminders_from_prescription

def test_reminder_generator():
    """Test the reminder generator with sample prescription data"""
    
    print("=" * 80)
    print("TESTING PRESCRIPTION TO REMINDER CONVERSION")
    print("=" * 80)
    
    # Sample prescription data (similar to what AI would extract)
    sample_prescription = {
        "patient_info": {
            "name": "ហុ ចាន",
            "id": "HAKF1354164",
            "age": 19,
            "gender": "ស្រី",
            "hospital_code": "HAKF"
        },
        "medical_info": {
            "diagnosis": "Chronic Cystitis",
            "doctor": "Srvheng",
            "date": "15/06/2025",
            "department": "បន្ទប់លេខ 5"
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
    
    print("\n📋 INPUT PRESCRIPTION DATA:")
    print(f"   Patient: {sample_prescription['patient_info']['name']} (Age: {sample_prescription['patient_info']['age']})")
    print(f"   Diagnosis: {sample_prescription['medical_info']['diagnosis']}")
    print(f"   Medications: {len(sample_prescription['medications'])}")
    
    for i, med in enumerate(sample_prescription['medications'], 1):
        print(f"   {i}. {med['name']} - {med['schedule']['frequency']} ({', '.join(med['schedule']['times'])})")
    
    # Generate reminders
    print("\n🔄 GENERATING REMINDERS...")
    result = generate_reminders_from_prescription(sample_prescription, "2025-06-15")
    
    # Display results
    print("\n✅ GENERATION RESULTS:")
    print(f"   Success: {result.get('validation', {}).get('valid', False)}")
    print(f"   Total Reminders: {result['metadata']['total_reminders']}")
    print(f"   Total Medications: {result['metadata']['total_medications']}")
    print(f"   Start Date: {result['metadata']['start_date']}")
    
    if result.get('validation', {}).get('errors'):
        print(f"\n⚠️  Validation Errors:")
        for error in result['validation']['errors']:
            print(f"   - {error}")
    
    if result.get('validation', {}).get('warnings'):
        print(f"\n⚠️  Validation Warnings:")
        for warning in result['validation']['warnings']:
            print(f"   - {warning}")
    
    # Display generated reminders
    print("\n📅 GENERATED REMINDERS:")
    print("-" * 80)
    
    for i, reminder in enumerate(result['reminders'], 1):
        print(f"\n{i}. {reminder['medication_name']}")
        print(f"   Time Slot: {reminder['time_slot']} ({reminder['scheduled_time']})")
        print(f"   Dose: {reminder['dose_amount']} {reminder['dose_unit']}")
        print(f"   Duration: {reminder['start_date']} to {reminder['end_date']}")
        print(f"   Notification: {reminder['notification_title']}")
        print(f"   Body: {reminder['notification_body']}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    # Save results to file
    output_file = '/home/rayu/DasTern/test_reminder_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return result

def test_time_slot_mapping():
    """Test Khmer time slot mapping"""
    print("\n" + "=" * 80)
    print("TESTING TIME SLOT MAPPING")
    print("=" * 80)
    
    generator = ReminderGenerator()
    
    test_cases = [
        ["ព្រឹក", "ល្ងាច"],
        ["morning", "evening"],
        ["matin", "soir"],
        ["ថ្ងៃត្រង់", "យប់"],
        ["noon", "night"]
    ]
    
    print("\n🕐 Time Slot Conversions:")
    for times in test_cases:
        converted = generator._convert_times_to_24h(times)
        print(f"   {times} → {converted}")
    
    print("\n✅ Time slot mapping test completed!")

if __name__ == "__main__":
    try:
        # Test reminder generation
        result = test_reminder_generator()
        
        # Test time slot mapping
        test_time_slot_mapping()
        
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
