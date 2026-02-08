#!/usr/bin/env python3
"""
Simple test to verify AI service is working
Uses a basic English prescription for fast testing
"""

import requests
import time

print("\n" + "="*70)
print("🧪 TESTING AI ENHANCEMENT SERVICE")
print("="*70)

# Simple test data
test_data = {
    "raw_ocr_json": {
        "raw_text": "Amoxicillin 500mg. Take 1 capsule 3 times daily for 7 days.",
        "blocks": [{
            "text": "Amoxicillin 500mg. Take 1 capsule 3 times daily for 7 days."
        }]
    }
}

print("\n📝 Test prescription: Amoxicillin 500mg, 3x daily, 7 days")
print("⏳ Processing... (10-30 seconds)\n")

start = time.time()

try:
    response = requests.post(
        "http://localhost:8001/extract-reminders",
        json=test_data,
        timeout=90
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS in {elapsed:.1f} seconds\n")
        print("="*70)
        
        if result.get('success') and result.get('medications'):
            meds = result['medications']
            print(f"✅ Extracted {len(meds)} medication(s):\n")
            
            for i, med in enumerate(meds, 1):
                print(f"  Medication #{i}:")
                print(f"    Name:     {med.get('name')}")
                print(f"    Dosage:   {med.get('dosage')}")
                print(f"    Times:    {', '.join(med.get('times', []))}")
                print(f"    Duration: {med.get('duration_days')} days")
                print()
            
            print("="*70)
            print("✅ AI SERVICE IS WORKING!")
            print("="*70)
            print("\n💡 Next step: Test with Flutter app")
            print("   cd ocr_ai_for_reminder && flutter run")
            
        else:
            print(f"⚠️  No medications extracted")
            print(f"   Success: {result.get('success')}")
            print(f"   Error: {result.get('error')}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"   {response.text[:200]}")
        
except requests.Timeout:
    print(f"❌ TIMEOUT after {time.time() - start:.1f}s")
    print("   AI service may need more time or higher timeout")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
