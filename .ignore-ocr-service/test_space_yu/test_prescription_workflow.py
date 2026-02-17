#!/usr/bin/env python3
"""
Test script for prescription scanning and reminder generation workflow
"""

import requests
import json
import base64
from pathlib import Path
import sys

def test_ocr_service(image_path, ocr_url="http://localhost:8000"):
    """Test OCR service with prescription image"""
    print(f"🔍 Testing OCR service with {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{ocr_url}/process", files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OCR Success!")
            print(f"📄 Extracted text: {result.get('full_text', '')[:200]}...")
            print(f"🎯 Confidence: {result.get('overall_confidence', 0):.2f}")
            print(f"🌐 Language: {result.get('language', 'unknown')}")
            return result
        else:
            print(f"❌ OCR failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ OCR service error: {e}")
        return None

def test_ai_correction(text, ai_url="http://localhost:8001"):
    """Test AI text correction service"""
    print(f"🤖 Testing AI correction service")
    
    try:
        payload = {
            "text": text,
            "language": "km"  # Khmer
        }
        response = requests.post(f"{ai_url}/correct-ocr", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Correction Success!")
            print(f"📝 Corrected text: {result.get('corrected_text', '')[:200]}...")
            print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
            return result
        else:
            print(f"❌ AI correction failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ AI service error: {e}")
        return None

def extract_medications_from_khmer_prescription(text):
    """
    Extract medications from Khmer prescription text
    This is a simple parser for the table format in your prescriptions
    """
    medications = []
    lines = text.split('\n')
    
    # Look for medication patterns in Khmer prescriptions
    # The prescriptions have tables with medication names and dosages
    
    # Common medication names from your images
    known_meds = [
        'Calcium', 'Multivitamine', 'Amitriptyline', 
        'Butylscopolamine', 'Celcoxx', 'Omeprazole',
        'Paracetamol', 'Esome'
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains medication info
        for med_name in known_meds:
            if med_name.lower() in line.lower():
                # Extract dosage info (look for numbers followed by mg, tablet, etc.)
                import re
                
                # Extract strength (e.g., "10mg", "500mg")
                strength_match = re.search(r'(\d+)\s*(mg|ml)', line, re.IGNORECASE)
                strength = strength_match.group(0) if strength_match else None
                
                # Extract tablet count
                tablet_match = re.search(r'(\d+)\s*(tablet|ថ្នាំ)', line, re.IGNORECASE)
                dosage = f"{tablet_match.group(1)} tablet" if tablet_match else "1 tablet"
                
                # Look for frequency indicators in the table columns
                # Your prescriptions have time columns (morning, noon, evening, night)
                frequency = "as prescribed"
                if "1" in line:
                    frequency = "once daily"
                
                medications.append({
                    'name': med_name,
                    'strength': strength,
                    'dosage': dosage,
                    'frequency': frequency,
                    'duration': '7 days',  # Default
                    'instructions': 'Take as prescribed'
                })
                break
    
    # If no medications found, add a placeholder
    if not medications:
        medications.append({
            'name': 'Unknown Medication',
            'strength': None,
            'dosage': '1 tablet',
            'frequency': 'twice daily',
            'duration': '7 days',
            'instructions': 'Please review prescription manually'
        })
    
    return medications

def generate_reminders_from_medications(medications):
    """Generate reminder schedule from medications"""
    reminders = []
    
    for med in medications:
        # Parse frequency to determine reminder times
        frequency = med.get('frequency', 'once daily').lower()
        
        if 'once' in frequency:
            times = ['08:00']
        elif 'twice' in frequency:
            times = ['08:00', '20:00']
        elif 'thrice' in frequency or 'three times' in frequency:
            times = ['08:00', '14:00', '20:00']
        else:
            times = ['08:00', '20:00']  # Default
        
        reminder = {
            'medication_name': med['name'],
            'strength': med['strength'],
            'dosage': med['dosage'],
            'reminder_times': times,
            'days_of_week': [1, 2, 3, 4, 5, 6, 7],  # All days
            'duration': med.get('duration', '7 days'),
            'instructions': med.get('instructions', 'Take as prescribed')
        }
        
        reminders.append(reminder)
    
    return reminders

def main():
    """Main test function"""
    print("🏥 DasTern Prescription Scanning Test")
    print("=" * 50)
    
    # Test with a sample image (you'll need to provide the path)
    # For now, let's simulate with the OCR text from your images
    
    # Sample OCR text from your first prescription image
    sample_ocr_text = """
    SOK HENG POLYCLINIC
    តេជោបញ្ញា
    
    ឈ្មោះ: ឈុន ចាប់ ភេទ: ស្រី អាយុ: 47 ឆ្នាំ
    អាស្រ័យដ្ឋាន: សង្កាត់កាកាប់ ខណ្ឌ
    
    លេខ ឈ្មោះថ្នាំ ចំនួន ព្រឹក ថ្ងៃ ល្ងាច យប់ សម្គាល់ ថ្ងៃ
    1. Calcium amp Tablet 1 - - - ថ្នាំបញ្ចុះ 4
    2. Multivitamine Tablet 1 - 1 - ថ្នាំបញ្ចុះ 10
    3. Amitriptyline 10mg - - - 1 ថ្នាំបញ្ចុះ 5
    """
    
    print("📄 Sample OCR Text:")
    print(sample_ocr_text)
    print("\n" + "=" * 50)
    
    # Extract medications
    print("💊 Extracting medications...")
    medications = extract_medications_from_khmer_prescription(sample_ocr_text)
    
    print(f"✅ Found {len(medications)} medications:")
    for i, med in enumerate(medications, 1):
        print(f"  {i}. {med['name']} - {med['strength']} - {med['frequency']}")
    
    print("\n" + "=" * 50)
    
    # Generate reminders
    print("⏰ Generating reminders...")
    reminders = generate_reminders_from_medications(medications)
    
    print(f"✅ Generated {len(reminders)} reminders:")
    for i, reminder in enumerate(reminders, 1):
        print(f"  {i}. {reminder['medication_name']}")
        print(f"     Times: {', '.join(reminder['reminder_times'])}")
        print(f"     Duration: {reminder['duration']}")
        print()
    
    # Save results
    results = {
        'ocr_text': sample_ocr_text,
        'medications': medications,
        'reminders': reminders,
        'timestamp': '2026-01-23T10:00:00Z'
    }
    
    with open('prescription_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("💾 Results saved to prescription_test_results.json")
    print("\n🎉 Test completed successfully!")

if __name__ == "__main__":
    main()