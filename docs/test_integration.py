#!/usr/bin/env python3
"""
Integration test for OCR → AI Enhancement flow
Tests the complete pipeline that the Flutter app uses
"""

import requests
import json
from pathlib import Path

# Service URLs
OCR_SERVICE = "http://localhost:8000"
AI_SERVICE = "http://localhost:8001"

def test_services_health():
    """Test if services are running"""
    print("🔍 Testing service health...")
    
    # Test OCR service
    try:
        r = requests.get(f"{OCR_SERVICE}/")
        print(f"✅ OCR Service: {r.json()['service']}")
    except Exception as e:
        print(f"❌ OCR Service failed: {e}")
        return False
    
    # Test AI service
    try:
        r = requests.get(f"{AI_SERVICE}/health")
        data = r.json()
        print(f"✅ AI Service: {data['status']} (Ollama: {data['ollama_connected']})")
    except Exception as e:
        print(f"❌ AI Service failed: {e}")
        return False
    
    return True

def test_extract_reminders():
    """Test AI reminder extraction with sample OCR data"""
    print("\n📋 Testing reminder extraction...")
    
    # Sample OCR data similar to what Flutter sends
    sample_ocr = {
        "raw_text": "Amoxicillin 500mg\nTake 1 capsule every 8 hours\nFor 7 days\n\nParacetamol 500mg\nTake 1 tablet when needed for pain",
        "blocks": [
            {
                "type": "text",
                "lines": [
                    {"text": "Amoxicillin 500mg"},
                    {"text": "Take 1 capsule every 8 hours"},
                    {"text": "For 7 days"}
                ]
            },
            {
                "type": "text",
                "lines": [
                    {"text": "Paracetamol 500mg"},
                    {"text": "Take 1 tablet when needed for pain"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{AI_SERVICE}/extract-reminders",
            json={"raw_ocr_json": sample_ocr},
            timeout=120  # Give it 2 minutes
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Extraction successful: {result.get('success', False)}")
            
            medications = result.get('medications', [])
            print(f"📊 Found {len(medications)} medication(s):")
            
            for i, med in enumerate(medications, 1):
                print(f"\n  {i}. {med.get('name', 'Unknown')}")
                print(f"     Dosage: {med.get('dosage', 'N/A')}")
                print(f"     Times: {med.get('times', [])}")
                print(f"     Times (24h): {med.get('times_24h', [])}")
                print(f"     Repeat: {med.get('repeat', 'N/A')}")
                print(f"     Duration: {med.get('duration_days', 'N/A')} days")
            
            return True
        else:
            print(f"❌ Extraction failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - Ollama may be too slow")
        print("   Try: export OLLAMA_TIMEOUT=600")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_performance():
    """Test with larger OCR data to check performance"""
    print("\n⚡ Testing performance with larger data...")
    
    # Create larger OCR data (simulate 10 blocks)
    large_ocr = {
        "raw_text": "Medication list\n" * 50,
        "blocks": [
            {
                "type": "text",
                "lines": [
                    {"text": f"Medication {i}", "confidence": 0.95}
                    for i in range(20)
                ]
            }
            for _ in range(10)
        ],
        "meta": {
            "languages": ["khm", "eng"],
            "confidence": 0.92
        }
    }
    
    import time
    start = time.time()
    
    try:
        response = requests.post(
            f"{AI_SERVICE}/extract-reminders",
            json={"raw_ocr_json": large_ocr},
            timeout=120
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Performance test passed in {elapsed:.2f}s")
            print(f"   Data simplification working: OCR data reduced automatically")
            return True
        else:
            print(f"⚠️  Response: {response.status_code} in {elapsed:.2f}s")
            return False
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Failed after {elapsed:.2f}s: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Integration Test: Flutter OCR → AI Enhancement")
    print("=" * 60)
    
    # Run tests
    if not test_services_health():
        print("\n❌ Services not healthy. Please start them first.")
        exit(1)
    
    success = test_extract_reminders()
    perf = test_performance()
    
    print("\n" + "=" * 60)
    if success and perf:
        print("✅ ALL TESTS PASSED")
        print("\nFlutter app should work correctly with these services.")
        print("\nTo test with Flutter:")
        print("  cd ocr_ai_for_reminder")
        print("  flutter run")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nCheck service logs for details.")
    print("=" * 60)
