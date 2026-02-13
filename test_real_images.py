#!/usr/bin/env python3
"""
Test Prescription Analysis with Real Images
Processes images from OCR_Test_Space/images and saves results to results/
"""

import requests
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
IMAGES_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/images")
RESULTS_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/results")
BACKEND_URL = "http://localhost:3000"

# Ensure results directory exists
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def test_image(image_path: Path, result_number: int):
    """Test a single prescription image"""
    
    print(f"\n{'='*100}")
    print(f"TESTING IMAGE {result_number}: {image_path.name}")
    print(f"{'='*100}")
    
    result_file = RESULTS_DIR / f"result_reminder_{result_number}.json"
    
    try:
        # Check if file exists and is readable
        if not image_path.exists():
            print(f"❌ Error: Image file not found: {image_path}")
            return False
        
        file_size = image_path.stat().st_size
        print(f"📁 File: {image_path.name}")
        print(f"📊 Size: {file_size / 1024:.1f} KB")
        
        # Prepare the request
        url = f"{BACKEND_URL}/api/prescriptions/analyze"
        
        print(f"\n📤 Sending to: {url}")
        print(f"⏳ Processing... (this may take 30-60 seconds)")
        
        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f, 'image/png')}
            response = requests.post(url, files=files, timeout=120)
        
        # Process response
        if response.status_code == 200:
            result = response.json()
            
            # Add metadata
            result['test_metadata'] = {
                'image_file': image_path.name,
                'image_size_bytes': file_size,
                'test_timestamp': datetime.now().isoformat(),
                'result_number': result_number,
                'backend_url': BACKEND_URL
            }
            
            # Save result
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ SUCCESS!")
            print(f"💾 Result saved to: {result_file}")
            
            # Print summary
            if result.get('success'):
                summary = result.get('summary', {})
                print(f"\n📊 ANALYSIS SUMMARY:")
                print(f"   Analysis Type: {result.get('analysis_type', 'unknown')}")
                print(f"   Total Medications: {summary.get('total_medications', 0)}")
                print(f"   Total Reminders: {summary.get('total_reminders', 0)}")
                print(f"   Confidence Score: {summary.get('confidence_score', 0):.2f}")
                
                if result.get('ocr_data'):
                    ocr = result['ocr_data']
                    print(f"\n📝 OCR DATA:")
                    print(f"   Confidence: {ocr.get('confidence', 0):.2f}")
                    print(f"   Language: {ocr.get('language', 'unknown')}")
                    text_preview = ocr.get('raw_text', '')[:200]
                    print(f"   Text Preview: {text_preview}...")
                
                if result.get('ai_enhancement'):
                    ai = result['ai_enhancement']
                    meta = ai.get('metadata', {})
                    print(f"\n🤖 AI ENHANCEMENT:")
                    print(f"   Model: {meta.get('model_used', 'unknown')}")
                    print(f"   Confidence: {meta.get('confidence_score', 0):.2f}")
                    print(f"   Total Reminders: {meta.get('total_reminders', 0)}")
                    
                    meds = ai.get('prescription', {}).get('medications', [])
                    if meds:
                        print(f"\n💊 MEDICATIONS FOUND:")
                        for i, med in enumerate(meds[:5], 1):  # Show first 5
                            schedule = med.get('schedule', {})
                            times = schedule.get('times', [])
                            print(f"   {i}. {med.get('name', 'Unknown')}")
                            print(f"      Schedule: {', '.join(times) if times else 'N/A'}")
                
                if result.get('analysis'):
                    analysis = result['analysis']
                    quality = analysis.get('extraction_quality', {})
                    print(f"\n🔍 QUALITY ASSESSMENT:")
                    print(f"   OCR Quality: {quality.get('ocr_quality', 'unknown')} ({quality.get('ocr_confidence', 0):.2f})")
                    if quality.get('ai_quality'):
                        print(f"   AI Quality: {quality.get('ai_quality')} ({quality.get('ai_confidence', 0):.2f})")
                    
                    recs = analysis.get('recommendations', [])
                    if recs:
                        print(f"\n💡 RECOMMENDATIONS:")
                        for rec in recs[:3]:
                            print(f"   • {rec}")
                
                return True
            else:
                print(f"\n⚠️  Analysis returned success=false")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
            # Save error result
            error_result = {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'response_text': response.text,
                'test_metadata': {
                    'image_file': image_path.name,
                    'test_timestamp': datetime.now().isoformat(),
                    'result_number': result_number
                }
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)
            
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print(f"   Is the backend running on {BACKEND_URL}?")
        print(f"   Start with: cd backend-nextjs && npm run dev")
        return False                                                                                
    except requests.exceptions.Timeout:
        print(f"\n⏱️  Timeout Error: Request took too long")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("="*100)
    print("PRESCRIPTION ANALYSIS TEST - REAL IMAGES")
    print("="*100)
    print(f"\n📁 Images Directory: {IMAGES_DIR}")
    print(f"📁 Results Directory: {RESULTS_DIR}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    
    # Find all images
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    images = [f for f in IMAGES_DIR.iterdir() 
              if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"\n❌ No images found in {IMAGES_DIR}")
        print(f"   Supported formats: {', '.join(image_extensions)}")
        sys.exit(1)
    
    print(f"\n📸 Found {len(images)} image(s) to test:")
    for i, img in enumerate(images, 1):
        size = img.stat().st_size / 1024
        print(f"   {i}. {img.name} ({size:.1f} KB)")
    
    # Test each image
    results = []
    for i, image_path in enumerate(images, 1):
        success = test_image(image_path, i)
        results.append({
            'image': image_path.name,
            'result_number': i,
            'success': success
        })
    
    # Summary
    print(f"\n{'='*100}")
    print("TEST SUMMARY")
    print(f"{'='*100}")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n📊 Results:")
    print(f"   Total Tests: {len(results)}")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    
    print(f"\n💾 Saved Results:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"   {status} result_reminder_{r['result_number']}.json ({r['image']})")
    
    print(f"\n📂 Results Location: {RESULTS_DIR}")
    
    if successful > 0:
        print(f"\n🎉 Testing completed! Check the JSON files for detailed results.")
    else:
        print(f"\n⚠️  All tests failed. Check if services are running.")
    
    return successful > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
