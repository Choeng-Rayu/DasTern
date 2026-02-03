#!/usr/bin/env python3
"""
Test script for new structured reminder AI
Tests the enhanced AI service with OCR data
"""
import json
import requests
from pathlib import Path

# Configuration
AI_SERVICE_URL = "http://localhost:8001"

def test_structured_reminders():
    """Test the new structured reminder endpoint"""
    
    # Example raw OCR data (from your previous test)
    raw_ocr_data = {
        "text": "លេខកូដ: HAKF 1354164 ឈ្មោះអ្នកជំងឺ: ង៉ាំ ដានី អាយុ: 19 ឆ្នាំ ភេទ: ស្រី ប្រភេទបង់ប្រាត់ : មូលនិនិសមធម៌ / 20051002-0409 ni ae រោគវិនិច្ឆ័យ : Chronic Cystiti fin q ironic Cystitis eee | ផ្នែក : ពិគ្រោះជំងឺក្រៅ - បន្ទប់លេខ 5 វេជ្ជបញ្ជា : din ល្ងាច | យប់ ន ឈ្មោះឱសថ ចំនួន វិធីប្រើ (68) (05-06) | (08-10) Butylscopolami 5 ន បយ បឬយ272@777ញាញយាយាយ យ RIRES ER ES រាជធានីភ្នំពេញ,ថ្ងៃទី 15/06/2025 14:20 គ្រពេទ្យព្យាបាល Suh | សូមយកវេដ្ជបញ្ជាមកវិញ ពេលពិនិត្យលើកក្រោយ វេជ្ជបណ្ឌិត យុយ ស៊ីវហេង",
        "confidence": 0.73,
        "source_file": "image.png"
    }
    
    # STEP 6: Example test case
    test_case = {
        "raw_ocr_json": raw_ocr_data
    }
    
    print("🎯 Testing Structured Reminder Extraction")
    print("=" * 50)
    print(f"📄 Raw OCR text snippet: {raw_ocr_data['text'][:100]}...")
    print()
    
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/extract-reminders",
            json=test_case,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! AI processed OCR data")
            print(f"📊 Success status: {result.get('success', False)}")
            
            if result.get('success'):
                medications = result.get('medications', [])
                print(f"💊 Found {len(medications)} medication(s)")
                
                for i, med in enumerate(medications, 1):
                    print(f"\n📋 Medication {i}:")
                    print(f"  Name: {med.get('name', 'Unknown')}")
                    print(f"  Times: {med.get('times', [])}")
                    print(f"  24h Times: {med.get('times_24h', [])}")
                    print(f"  Repeat: {med.get('repeat', 'daily')}")
                    print(f"  Duration: {med.get('duration_days', 'Not specified')}")
                    print(f"  Notes: {med.get('notes', '')}")
                    
                    # Validate structure
                    times = med.get('times', [])
                    times_24h = med.get('times_24h', [])
                    if len(times) == len(times_24h):
                        print("  ✅ Time arrays match correctly")
                    else:
                        print("  ❌ Time arrays mismatch!")
            else:
                print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (30s)")
    except Exception as e:
        print(f"💥 Request failed: {str(e)}")
    
    print("\n" + "=" * 50)

def test_simple_case():
    """Test with the simple example from your guide"""
    print("🧪 Testing Simple Example Case")
    print("=" * 50)
    
    # STEP 6: Your example
    simple_test = {
        "raw_ocr_json": {
            "text": "Butylscopolami 5 viên | ល្ងាច | យប់",
            "confidence": 0.8
        }
    }
    
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/extract-reminders",
            json=simple_test,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simple case processed!")
            
            if result.get('success'):
                medications = result.get('medications', [])
                if medications:
                    med = medications[0]
                    print(f"📋 Expected: Butylscopolamine, evening+night")
                    print(f"📋 Got: {med.get('name')}, {med.get('times')}")
                    
                    # Check if it matches expected output
                    expected_times = ["evening", "night"]
                    expected_24h = ["18:00", "21:00"]
                    
                    if (med.get('times') == expected_times and 
                        med.get('times_24h') == expected_24h):
                        print("🎉 Perfect match with expected output!")
                    else:
                        print("⚠️  Output differs from expected")
                        print(f"   Expected times: {expected_times}")
                        print(f"   Expected 24h: {expected_24h}")
                        
            print(f"📄 Full response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
    except Exception as e:
        print(f"💥 Simple test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced AI Service with Structured Reminders")
    print("=" * 60)
    
    # Test the simple example first
    test_simple_case()
    print()
    
    # Test with real OCR data
    test_structured_reminders()
    
    print("\n🏁 Testing complete!")
    print("\n📋 Next steps:")
    print("1. ✅ Verify JSON structure is correct")
    print("2. ✅ Check time normalization works")
    print("3. ✅ Validate Khmer text processing")
    print("4. ✅ Test with different OCR inputs")