#!/usr/bin/env python3
"""
Simple test for structured reminder extraction
Tests with minimal data to verify the system works
"""
import json
import requests

# Configuration
AI_SERVICE_URL = "http://localhost:8001"

def test_minimal_case():
    """Test with the simplest possible case"""
    print("🧪 Testing Minimal Case")
    print("=" * 40)
    
    # Very simple test case
    simple_test = {
        "raw_ocr_json": {
            "text": "Paracetamol ព្រឹក",
            "confidence": 0.9
        }
    }
    
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/extract-reminders",
            json=simple_test,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received!")
            print(f"📊 Success: {result.get('success', False)}")
            
            if result.get('success'):
                medications = result.get('medications', [])
                print(f"💊 Found {len(medications)} medication(s)")
                
                if medications:
                    med = medications[0]
                    print(f"📋 Name: {med.get('name')}")
                    print(f"📋 Times: {med.get('times')}")
                    print(f"📋 24h: {med.get('times_24h')}")
                    
                    # Check if it matches expected
                    if med.get('times') == ['morning'] and med.get('times_24h') == ['08:00']:
                        print("🎉 Perfect! Time normalization works!")
                    else:
                        print("⚠️  Time normalization needs adjustment")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
            print(f"📄 Full response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Test failed: {str(e)}")

def test_direct_ollama():
    """Test Ollama directly to see if it's working"""
    print("\n🔧 Testing Ollama Directly")
    print("=" * 40)
    
    try:
        payload = {
            "model": "llama3.2:3b",
            "prompt": "Convert 'ព្រឹក' to English time word. Answer only: morning",
            "stream": False,
            "options": {
                "temperature": 0.2,
                "max_tokens": 10
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ollama response: {result.get('response', '').strip()}")
        else:
            print(f"❌ Ollama error: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Ollama test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Simple Structured Reminder Test")
    print("=" * 50)
    
    # Test Ollama first
    test_direct_ollama()
    
    # Test our service
    test_minimal_case()
    
    print("\n🏁 Test complete!")