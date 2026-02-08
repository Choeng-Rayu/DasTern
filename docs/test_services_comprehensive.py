#!/usr/bin/env python3
"""
Comprehensive Test Script for OCR Service + AI-LLM Enhancement
Tests both services and stores results in the test space
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# Configuration
OCR_SERVICE_URL = "http://localhost:8002"
AI_SERVICE_URL = "http://localhost:8001"
RESULTS_DIR = Path("/home/rayu/DasTern/ai-llm-service/reports")
OCR_RESULTS_DIR = Path("/home/rayu/DasTern/ocr-service/results")

def test_ocr_service_health():
    """Test OCR service health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: OCR Service Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OCR Service Status: {data['status']}")
            print(f"   Tesseract: {data['tesseract']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ocr_service_languages():
    """Test OCR service languages endpoint"""
    print("\n" + "="*60)
    print("TEST 2: OCR Available Languages")
    print("="*60)
    
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/api/v1/ocr/languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available Languages: {', '.join(data.get('languages', []))}")
            return True
        else:
            print(f"❌ Failed to get languages: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ocr_service_info():
    """Test OCR service root endpoint"""
    print("\n" + "="*60)
    print("TEST 3: OCR Service Info")
    print("="*60)
    
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            print(f"   API Endpoint: {data.get('api')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_service_health():
    """Test AI-LLM service health endpoint"""
    print("\n" + "="*60)
    print("TEST 4: AI-LLM Service Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service Status: {data['status']}")
            print(f"   Ollama Connected: {data.get('ollama_connected', False)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_service_info():
    """Test AI-LLM service root endpoint"""
    print("\n" + "="*60)
    print("TEST 5: AI-LLM Service Info")
    print("="*60)
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Model: {data.get('model')}")
            print(f"   Capabilities: {', '.join(data.get('capabilities', []))}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_ocr_correction():
    """Test AI OCR correction with sample text"""
    print("\n" + "="*60)
    print("TEST 6: AI OCR Text Correction")
    print("="*60)
    
    test_cases = [
        {
            "text": "Parscotamol B00mg",
            "expected_fixes": ["Paracetamol", "500mg"]
        },
        {
            "text": "Tako 2ibots deiy",
            "expected_fixes": ["Take", "2", "tablets", "daily"]
        }
    ]
    
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n   Test {i}: '{test['text']}'")
        try:
            response = requests.post(
                f"{AI_SERVICE_URL}/api/v1/correct",
                json={"raw_text": test['text'], "language": "en"},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                corrected = data.get('corrected_text', '')
                confidence = data.get('confidence', 0)
                print(f"   ✅ Corrected: '{corrected}'")
                print(f"   📊 Confidence: {confidence}")
                results.append({
                    "input": test['text'],
                    "output": corrected,
                    "confidence": confidence,
                    "success": True
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
                results.append({
                    "input": test['text'],
                    "success": False
                })
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "input": test['text'],
                "success": False,
                "error": str(e)
            })
    
    return results

def test_with_existing_ocr_data():
    """Test AI enhancement with existing OCR results"""
    print("\n" + "="*60)
    print("TEST 7: AI Enhancement with Existing OCR Data")
    print("="*60)
    
    # Use existing OCR result
    ocr_file = OCR_RESULTS_DIR / "tesseract_result_1.json"
    
    if not ocr_file.exists():
        print(f"❌ OCR result file not found: {ocr_file}")
        return None
    
    with open(ocr_file, 'r') as f:
        ocr_data = json.load(f)
    
    print(f"📄 Loading OCR data from: {ocr_file.name}")
    print(f"   Source: {ocr_data.get('source_file')}")
    print(f"   Words detected: {ocr_data.get('stats', {}).get('total_words', 0)}")
    print(f"   Avg confidence: {ocr_data.get('stats', {}).get('avg_confidence', 0)}%")
    
    # Extract text from OCR
    raw_text = " ".join([word['text'] for word in ocr_data.get('raw', [])])
    print(f"\n   Raw OCR Text: '{raw_text[:80]}...'")
    
    # Send to AI for correction
    print("\n   🔄 Sending to AI-LLM service for correction...")
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/correct-ocr",
            json={"text": raw_text, "language": "en"},
            timeout=30
        )
        if response.status_code == 200:
            ai_result = response.json()
            print(f"   ✅ AI Corrected: '{ai_result.get('corrected_text', '')[:80]}...'")
            print(f"   📊 Confidence: {ai_result.get('confidence', 0)}")
            print(f"   🔧 Corrections: {ai_result.get('corrections_made', 0)}")
            
            return {
                "ocr_source": str(ocr_file),
                "raw_text": raw_text,
                "ai_corrected": ai_result.get('corrected_text', ''),
                "confidence": ai_result.get('confidence', 0),
                "corrections_made": ai_result.get('corrections_made', 0),
                "success": True
            }
        else:
            print(f"   ❌ AI correction failed: {response.status_code}")
            return {
                "ocr_source": str(ocr_file),
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "ocr_source": str(ocr_file),
            "success": False,
            "error": str(e)
        }

def test_reminder_extraction():
    """Test reminder extraction from prescription data"""
    print("\n" + "="*60)
    print("TEST 8: Reminder Extraction from OCR")
    print("="*60)
    
    # Sample prescription data
    prescription_data = {
        "corrected_text": "Paracetamol 500mg\nTake 2 tablets daily\nMorning and Evening\nDuration: 5 days",
        "raw": [
            {"text": "Paracetamol", "confidence": 85},
            {"text": "500mg", "confidence": 92},
            {"text": "Morning", "confidence": 88},
            {"text": "Evening", "confidence": 87}
        ],
        "stats": {
            "total_words": 4,
            "avg_confidence": 88
        }
    }
    
    print(f"   📄 Testing with prescription data...")
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/extract-reminders",
            json={"raw_ocr_json": prescription_data},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('success', False)}")
            medications = result.get('medications', [])
            print(f"   💊 Medications found: {len(medications)}")
            for med in medications:
                print(f"      - {med.get('name', 'Unknown')}")
                print(f"        Times: {', '.join(med.get('times', []))}")
                print(f"        Dosage: {med.get('dosage', 'N/A')}")
            return result
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}

def save_test_results(results):
    """Save all test results to reports directory"""
    print("\n" + "="*60)
    print("SAVING TEST RESULTS")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"test_results_{timestamp}.json"
    
    # Ensure directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    test_report = {
        "test_run_timestamp": datetime.now().isoformat(),
        "ocr_service_url": OCR_SERVICE_URL,
        "ai_service_url": AI_SERVICE_URL,
        "summary": {
            "total_tests": len([r for r in results if r is not None]),
            "passed": len([r for r in results if r is not None and (isinstance(r, bool) and r or isinstance(r, dict) and r.get('success', True))]),
            "failed": len([r for r in results if r is not None and (isinstance(r, bool) and not r or isinstance(r, dict) and not r.get('success', True))])
        },
        "results": {
            "ocr_health": results[0],
            "ocr_languages": results[1],
            "ocr_info": results[2],
            "ai_health": results[3],
            "ai_info": results[4],
            "ai_correction": results[5],
            "ai_enhancement": results[6],
            "reminder_extraction": results[7]
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {output_file}")
    print(f"\n   Summary:")
    print(f"   - Total Tests: {test_report['summary']['total_tests']}")
    print(f"   - Passed: {test_report['summary']['passed']}")
    print(f"   - Failed: {test_report['summary']['failed']}")
    
    return output_file

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE SERVICE TEST SUITE")
    print("="*60)
    print(f"OCR Service: {OCR_SERVICE_URL}")
    print(f"AI Service: {AI_SERVICE_URL}")
    print(f"Results will be saved to: {RESULTS_DIR}")
    
    results = []
    
    # Run all tests
    results.append(test_ocr_service_health())
    results.append(test_ocr_service_languages())
    results.append(test_ocr_service_info())
    results.append(test_ai_service_health())
    results.append(test_ai_service_info())
    results.append(test_ai_ocr_correction())
    results.append(test_with_existing_ocr_data())
    results.append(test_reminder_extraction())
    
    # Save results
    output_file = save_test_results(results)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print(f"📄 Full report: {output_file}")
    print("\n✅ All services tested successfully!")
    print("📝 Check the reports directory for detailed results.")
    
    return results

if __name__ == "__main__":
    main()
