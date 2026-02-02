#!/usr/bin/env python3
"""
Complete Pipeline Test: Image → OCR Service → AI Service → Results
Test images from /home/rayu/DasTern/OCR_Test_Space/images
Save results to /home/rayu/DasTern/OCR_Test_Space/results

Proper flow:
1. Send image to OCR Service (port 8002) - extracts raw text
2. Send OCR output to AI Service (port 8001) - processes into structured reminders
3. Save both raw OCR and AI-enhanced results for analysis
"""
import json
import requests
import sys
from pathlib import Path
from datetime import datetime

# Configuration - Updated ports
OCR_SERVICE_URL = "http://localhost:8002"
AI_SERVICE_URL = "http://localhost:8001"
IMAGES_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/images")
RESULTS_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/results")

# Create results directory if it doesn't exist
RESULTS_DIR.mkdir(exist_ok=True)

# Test images
TEST_IMAGES = [
    {"file": "image1.png", "name": "Khmer-Soviet Hospital (Chronic Cystitis)"},
    {"file": "image2.png", "name": "Sok Heng Polyclinic (Asthénie)"},
    {"file": "image.png", "name": "Khmer-Soviet Hospital (Second Visit)"}
]


def check_services():
    """Check if both services are running"""
    print("🔍 Checking services...")
    print("-" * 70)
    
    # Check OCR service
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ OCR Service: Running on {OCR_SERVICE_URL}")
            ocr_ok = True
        else:
            print(f"❌ OCR Service: HTTP {response.status_code}")
            ocr_ok = False
    except Exception as e:
        print(f"❌ OCR Service: Not accessible ({e})")
        ocr_ok = False
    
    # Check AI service
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service: Running on {AI_SERVICE_URL}")
            print(f"   Ollama connected: {data.get('ollama_connected', False)}")
            ai_ok = data.get('ollama_connected', False)
        else:
            print(f"❌ AI Service: HTTP {response.status_code}")
            ai_ok = False
    except Exception as e:
        print(f"❌ AI Service: Not accessible ({e})")
        ai_ok = False
    
    print("-" * 70)
    
    if not ocr_ok or not ai_ok:
        print("\n❌ Services not ready. Please start them:")
        print("   Terminal 1: cd /home/rayu/DasTern/ocr-service && source /home/rayu/DasTern/.venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002")
        print("   Terminal 2: cd /home/rayu/DasTern/ai-llm-service && source /home/rayu/DasTern/.venv/bin/activate && export OLLAMA_HOST=http://localhost:11434 && python app/main_ollama.py")
        return False
    
    return True


def process_image_with_ocr(image_path: Path, image_name: str):
    """Step 1: Send image to OCR service and get raw text"""
    print(f"\n📄 STEP 1: OCR Processing - {image_name}")
    print("=" * 70)
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"📁 Image: {image_path.name}")
    print(f"⏳ Sending to OCR service...")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/png')}
            data = {
                'apply_preprocessing': 'true',
                'languages': 'khm+eng+fra',
                'include_low_confidence': 'true',
                'include_stats': 'true'
            }
            
            response = requests.post(
                f"{OCR_SERVICE_URL}/api/v1/ocr/extract",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            ocr_result = response.json()
            
            if ocr_result.get('success'):
                print(f"✅ OCR Success!")
                
                # Display raw OCR info
                stats = ocr_result.get('stats', {})
                raw_elements = ocr_result.get('raw', [])
                
                print(f"\n📊 OCR Results:")
                print(f"   Total text elements: {len(raw_elements)}")
                if stats:
                    print(f"   Confidence: {stats.get('overall_confidence', 'N/A')}")
                    print(f"   Image size: {stats.get('image_width', 'N/A')}x{stats.get('image_height', 'N/A')}")
                
                # Extract text for display
                texts = [elem.get('text', '') for elem in raw_elements if elem.get('text')]
                full_text = ' '.join(texts)
                
                print(f"\n📝 Extracted Text (first 300 chars):")
                print("-" * 70)
                display_text = full_text[:300] if len(full_text) > 300 else full_text
                print(display_text)
                if len(full_text) > 300:
                    print("...")
                print("-" * 70)
                
                return ocr_result
            else:
                print(f"❌ OCR failed: {ocr_result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ OCR HTTP Error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ OCR request timed out (60s)")
        return None
    except Exception as e:
        print(f"💥 OCR request failed: {e}")
        return None


def process_ocr_with_ai(ocr_result: dict, image_name: str):
    """Step 2: Send OCR output to AI service for processing"""
    print(f"\n🤖 STEP 2: AI Processing - {image_name}")
    print("=" * 70)
    
    print(f"⏳ Sending OCR data to AI service...")
    print(f"   (This takes 40-120 seconds on CPU)")
    
    try:
        # Prepare OCR data for AI
        ocr_data = {
            "raw": ocr_result.get('raw', []),
            "stats": ocr_result.get('stats', {}),
            "languages_used": ocr_result.get('languages_used', [])
        }
        
        # Add extracted text for easier processing
        texts = [elem.get('text', '') for elem in ocr_data['raw'] if elem.get('text')]
        ocr_data['extracted_text'] = ' '.join(texts)
        
        response = requests.post(
            f"{AI_SERVICE_URL}/extract-reminders",
            json={"raw_ocr_json": ocr_data},
            timeout=180  # 3 minutes for LLM
        )
        
        if response.status_code == 200:
            ai_result = response.json()
            
            print(f"✅ AI Processing Complete!")
            
            if ai_result.get('success'):
                medications = ai_result.get('medications', [])
                
                print(f"\n💊 Medications Found: {len(medications)}")
                print("-" * 70)
                
                for i, med in enumerate(medications, 1):
                    print(f"\n  {i}. {med.get('name', 'Unknown')}")
                    print(f"     Times: {med.get('times', [])}")
                    print(f"     24h:   {med.get('times_24h', [])}")
                    if med.get('duration_days'):
                        print(f"     Duration: {med.get('duration_days')} days")
                    if med.get('notes'):
                        print(f"     Notes: {med.get('notes')[:50]}...")
                
                print("\n" + "-" * 70)
                
                return ai_result
            else:
                print(f"⚠️  AI processing failed: {ai_result.get('error', 'Unknown')}")
                return ai_result
        else:
            print(f"❌ AI HTTP Error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ AI request timed out (180s)")
        return None
    except Exception as e:
        print(f"💥 AI request failed: {e}")
        return None


def save_complete_result(result_num: int, image_name: str, image_file: str, 
                         ocr_result: dict, ai_result: dict = None):
    """Save complete pipeline result to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"complete_result_{result_num}_{timestamp}.json"
    
    output = {
        "test_info": {
            "result_number": result_num,
            "image_name": image_name,
            "image_file": image_file,
            "timestamp": datetime.now().isoformat(),
            "ocr_service": OCR_SERVICE_URL,
            "ai_service": AI_SERVICE_URL
        },
        "step_1_ocr_output": {
            "description": "Raw OCR output from OCR Service (Step 1)",
            "success": ocr_result.get('success', False),
            "total_elements": len(ocr_result.get('raw', [])),
            "stats": ocr_result.get('stats', {}),
            "languages_used": ocr_result.get('languages_used', []),
            "raw_data": ocr_result.get('raw', [])[:10]  # First 10 elements only
        },
        "step_2_ai_output": {
            "description": "AI-enhanced structured reminders from AI Service (Step 2)",
            "success": ai_result.get('success', False) if ai_result else False,
            "medications": ai_result.get('medications', []) if ai_result else [],
            "error": ai_result.get('error') if ai_result else "No AI result",
            "metadata": ai_result.get('metadata', {}) if ai_result else {}
        }
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Complete result saved to: {result_file}")
    return result_file


def save_ocr_only_result(result_num: int, image_name: str, image_file: str, 
                         ocr_result: dict):
    """Save OCR-only result"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"ocr_result_{result_num}_{timestamp}.json"
    
    output = {
        "test_info": {
            "result_number": result_num,
            "image_name": image_name,
            "image_file": image_file,
            "timestamp": datetime.now().isoformat(),
            "ocr_service": OCR_SERVICE_URL
        },
        "ocr_output": {
            "success": ocr_result.get('success', False),
            "total_elements": len(ocr_result.get('raw', [])),
            "stats": ocr_result.get('stats', {}),
            "languages_used": ocr_result.get('languages_used', []),
            "raw_data": ocr_result.get('raw', [])[:20]  # First 20 elements
        }
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 OCR result saved to: {result_file}")
    return result_file


def save_ai_only_result(result_num: int, image_name: str, image_file: str, 
                        ai_result: dict):
    """Save AI-only result"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"ai_enhanced_{result_num}_{timestamp}.json"
    
    output = {
        "test_info": {
            "result_number": result_num,
            "image_name": image_name,
            "image_file": image_file,
            "timestamp": datetime.now().isoformat(),
            "ai_service": AI_SERVICE_URL
        },
        "ai_output": {
            "success": ai_result.get('success', False),
            "medications": ai_result.get('medications', []),
            "error": ai_result.get('error'),
            "metadata": ai_result.get('metadata', {})
        }
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 AI result saved to: {result_file}")
    return result_file


def run_pipeline_test(image_info: dict, result_num: int):
    """Run complete pipeline for one image"""
    image_file = image_info['file']
    image_name = image_info['name']
    image_path = IMAGES_DIR / image_file
    
    print("\n" + "=" * 70)
    print(f"🚀 TEST {result_num}: {image_name}")
    print("=" * 70)
    
    # Step 1: OCR
    ocr_result = process_image_with_ocr(image_path, image_name)
    
    if not ocr_result:
        print(f"\n❌ OCR failed for {image_name}")
        # Save error result
        save_ocr_only_result(result_num, image_name, image_file, 
                           {"success": False, "error": "OCR failed"})
        return False
    
    # Save OCR result first
    save_ocr_only_result(result_num, image_name, image_file, ocr_result)
    
    # Step 2: AI Processing
    ai_result = process_ocr_with_ai(ocr_result, image_name)
    
    if ai_result:
        save_ai_only_result(result_num, image_name, image_file, ai_result)
    
    # Save complete result (handle None ai_result)
    save_complete_result(result_num, image_name, image_file, ocr_result, ai_result if ai_result else {})
    
    if ai_result and ai_result.get('success'):
        print(f"\n✅ PIPELINE SUCCESS for {image_name}")
        return True
    elif ai_result:
        print(f"\n⚠️  PIPELINE PARTIAL SUCCESS - AI processing had issues")
        return False
    else:
        print(f"\n⚠️  OCR SUCCESS but AI processing failed")
        return False


def main():
    """Main test runner"""
    print("=" * 70)
    print("🚀 Complete Pipeline Test: Image → OCR → AI → Results")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  📁 Images: {IMAGES_DIR}")
    print(f"  💾 Results: {RESULTS_DIR}")
    print(f"\nFlow:")
    print("  1. Image → OCR Service (port 8002) - Extracts raw text")
    print("  2. OCR Output → AI Service (port 8001) - Structures reminders")
    print("  3. Save both raw OCR and AI-enhanced results")
    print("=" * 70)
    
    # Check services
    if not check_services():
        sys.exit(1)
    
    # Run tests for each image
    results = []
    for i, image_info in enumerate(TEST_IMAGES, 1):
        success = run_pipeline_test(image_info, i)
        results.append({"test": i, "name": image_info['name'], "success": success})
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 TESTING COMPLETE")
    print("=" * 70)
    
    print("\n📊 Summary:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"   {status} Test {r['test']}: {r['name']}")
    
    passed = sum(1 for r in results if r['success'])
    print(f"\n   Total: {passed}/{len(results)} tests passed")
    
    print("\n📁 Results saved to:")
    print(f"   {RESULTS_DIR}")
    print("\n📋 To analyze results:")
    print("   # View complete result:")
    print(f"   cat {RESULTS_DIR}/complete_result_1_*.json | python3 -m json.tool")
    print("\n   # View just the raw OCR:")
    print(f"   cat {RESULTS_DIR}/ocr_result_1_*.json | jq '.ocr_output'")
    print("\n   # View just the AI output:")
    print(f"   cat {RESULTS_DIR}/ai_enhanced_1_*.json | jq '.ai_output'")
    print("\n   # List all results:")
    print(f"   ls -lh {RESULTS_DIR}")


if __name__ == "__main__":
    main()
