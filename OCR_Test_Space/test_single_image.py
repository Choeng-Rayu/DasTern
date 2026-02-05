#!/usr/bin/env python3
"""
Test Single Image: Image → OCR → AI → Result
Tests one specific image through the complete pipeline
"""
import json
import requests
import sys
from pathlib import Path
from datetime import datetime

# Configuration
OCR_SERVICE_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"
IMAGES_DIR = Path(__file__).parent / "images"
RESULTS_DIR = Path(__file__).parent / "results"

# Create results directory if it doesn't exist
RESULTS_DIR.mkdir(exist_ok=True)


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
        print("   Terminal 1: cd /home/rayu/DasTern/ocr-service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("   Terminal 2: cd /home/rayu/DasTern/ai-llm-service && python -m uvicorn app.main_ollama:app --host 0.0.0.0 --port 8001")
        return False
    
    return True


def process_image(image_path: Path, image_name: str, result_num: int):
    """Process single image through OCR → AI pipeline"""
    print("\n" + "=" * 70)
    print(f"🚀 PROCESSING: {image_name}")
    print("=" * 70)
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return False
    
    # Step 1: OCR
    print(f"\n📄 STEP 1: OCR Processing")
    print("-" * 70)
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
            else:
                print(f"❌ OCR failed: {ocr_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ OCR HTTP Error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"💥 OCR request failed: {e}")
        return False
    
    # Step 2: AI Processing
    print(f"\n🤖 STEP 2: AI Processing")
    print("-" * 70)
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
            else:
                print(f"⚠️  AI processing failed: {ai_result.get('error', 'Unknown')}")
        else:
            print(f"❌ AI HTTP Error: {response.status_code}")
            ai_result = {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"💥 AI request failed: {e}")
        ai_result = {"success": False, "error": str(e)}
    
    # Save result
    result_file = RESULTS_DIR / f"result_{result_num}.json"
    output = {
        "test_info": {
            "result_number": result_num,
            "image_name": image_name,
            "image_file": image_path.name,
            "timestamp": datetime.now().isoformat(),
            "ocr_service": OCR_SERVICE_URL,
            "ai_service": AI_SERVICE_URL
        },
        "step_1_ocr_output": {
            "description": "Raw OCR output from OCR Service",
            "success": ocr_result.get('success', False),
            "total_elements": len(ocr_result.get('raw', [])),
            "stats": ocr_result.get('stats', {}),
            "languages_used": ocr_result.get('languages_used', []),
            "raw_data": ocr_result.get('raw', [])[:10]
        },
        "step_2_ai_output": {
            "description": "AI-enhanced structured reminders",
            "success": ai_result.get('success', False) if ai_result else False,
            "medications": ai_result.get('medications', []) if ai_result else [],
            "error": ai_result.get('error') if ai_result else None,
            "metadata": ai_result.get('metadata', {}) if ai_result else {}
        }
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Result saved to: {result_file}")
    
    if ai_result and ai_result.get('success'):
        print(f"\n✅ PIPELINE SUCCESS!")
        return True
    else:
        print(f"\n⚠️  PIPELINE COMPLETED WITH ISSUES")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_single_image.py <image_number>")
        print("")
        print("Available images:")
        print("  1 - image1.png (Khmer-Soviet Hospital - Chronic Cystitis)")
        print("  2 - image2.png (Sok Heng Polyclinic - Asthénie)")
        print("  3 - image.png (Khmer-Soviet Hospital - Second Visit)")
        print("")
        print("Example: python3 test_single_image.py 1")
        sys.exit(1)
    
    try:
        image_num = int(sys.argv[1])
    except ValueError:
        print("❌ Error: Please provide a number (1, 2, or 3)")
        sys.exit(1)
    
    # Map number to image
    image_map = {
        1: {"file": "image1.png", "name": "Khmer-Soviet Hospital (Chronic Cystitis)"},
        2: {"file": "image2.png", "name": "Sok Heng Polyclinic (Asthénie)"},
        3: {"file": "image.png", "name": "Khmer-Soviet Hospital (Second Visit)"}
    }
    
    if image_num not in image_map:
        print(f"❌ Error: Invalid image number {image_num}. Use 1, 2, or 3.")
        sys.exit(1)
    
    image_info = image_map[image_num]
    image_path = IMAGES_DIR / image_info['file']
    
    print("=" * 70)
    print("🚀 Single Image Pipeline Test")
    print("=" * 70)
    
    # Check services
    if not check_services():
        sys.exit(1)
    
    # Process the image
    success = process_image(image_path, image_info['name'], image_num)
    
    print("\n" + "=" * 70)
    print("🏁 TEST COMPLETE")
    print("=" * 70)
    print(f"\n📁 Result saved to: results/result_{image_num}.json")
    print("\n📋 To view result:")
    print(f"   cat results/result_{image_num}.json | python3 -m json.tool")


if __name__ == "__main__":
    main()
