#!/usr/bin/env python3
"""
Real OCR Service Test Script
Tests OCR service with actual images and stores results
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
OCR_SERVICE_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"
IMAGES_DIR = "/home/rayu/DasTern/.ignore-ocr-service/images_for_Test_yu"
RESULTS_DIR = "/home/rayu/DasTern/.ignore-ocr-service/test_space_yu"

def test_service_health():
    """Check if services are running"""
    print("=" * 60)
    print("CHECKING SERVICE HEALTH")
    print("=" * 60)
    
    # Check OCR service
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ OCR Service: HEALTHY")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ OCR Service: UNHEALTHY (Status {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ OCR Service: NOT REACHABLE ({e})")
        return False
    
    # Check AI service
    try:
        response = requests.get(f"{AI_SERVICE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✓ AI LLM Service: REACHABLE")
            print(f"  Response: {response.json()}")
        else:
            print(f"⚠ AI LLM Service: REACHABLE but status {response.status_code}")
    except Exception as e:
        print(f"⚠ AI LLM Service: NOT REACHABLE ({e})")
        print("  Will continue without AI enhancement")
    
    print()
    return True

def process_image(image_path):
    """Process a single image through OCR service"""
    image_name = os.path.basename(image_path)
    print(f"\n{'=' * 60}")
    print(f"PROCESSING: {image_name}")
    print(f"{'=' * 60}")
    
    try:
        # Read and send image
        with open(image_path, 'rb') as f:
            files = {'file': (image_name, f, 'image/png')}
            
            print(f"Sending request to {OCR_SERVICE_URL}/ocr...")
            response = requests.post(
                f"{OCR_SERVICE_URL}/ocr",
                files=files,
                timeout=60
            )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Add metadata
            result['test_metadata'] = {
                'image_name': image_name,
                'image_path': image_path,
                'test_timestamp': datetime.now().isoformat(),
                'ocr_service_url': OCR_SERVICE_URL,
                'response_status': response.status_code
            }
            
            # Check if AI enhanced
            ai_enhanced = result.get('ai_enhanced', False)
            if ai_enhanced:
                print("✓ Result includes AI enhancement")
            else:
                print("⚠ Result WITHOUT AI enhancement (AI service may not be ready)")
                result['ai_status'] = 'not_enhanced'
            
            # Print summary
            print(f"\nRESULT SUMMARY:")
            print(f"  - Blocks detected: {len(result.get('blocks', []))}")
            print(f"  - Overall confidence: {result.get('overall_confidence', 0):.2%}")
            print(f"  - Language: {result.get('language', 'unknown')}")
            print(f"  - AI Enhanced: {ai_enhanced}")
            
            if result.get('blocks'):
                print(f"\n  Top 5 text blocks:")
                for i, block in enumerate(result['blocks'][:5], 1):
                    text = block.get('text', '')[:50]
                    conf = block.get('confidence', 0)
                    print(f"    {i}. [{conf:.1%}] {text}")
            
            return result
        else:
            error_result = {
                'error': True,
                'status_code': response.status_code,
                'message': response.text,
                'image_name': image_name,
                'timestamp': datetime.now().isoformat()
            }
            print(f"✗ ERROR: {response.text}")
            return error_result
            
    except Exception as e:
        error_result = {
            'error': True,
            'exception': str(e),
            'image_name': image_name,
            'timestamp': datetime.now().isoformat()
        }
        print(f"✗ EXCEPTION: {e}")
        return error_result

def save_result(result, image_name):
    """Save result to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = image_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
    filename = f"ocr_test_{safe_name}_{timestamp}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Result saved to: {filename}")
    return filepath

def main():
    """Main test execution"""
    print("\n" + "=" * 60)
    print("OCR SERVICE REAL TESTING")
    print("=" * 60)
    print(f"Test started: {datetime.now().isoformat()}")
    print()
    
    # Check services
    if not test_service_health():
        print("\n✗ Services not ready. Please start services first.")
        return
    
    # Get all images
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        image_files.extend(Path(IMAGES_DIR).glob(ext))
    
    image_files = sorted(image_files)
    
    if not image_files:
        print(f"\n✗ No images found in {IMAGES_DIR}")
        return
    
    print(f"\nFound {len(image_files)} images to process")
    
    # Process each image
    all_results = []
    for image_path in image_files:
        result = process_image(str(image_path))
        if result:
            saved_path = save_result(result, image_path.name)
            all_results.append({
                'image': image_path.name,
                'result_file': os.path.basename(saved_path),
                'success': not result.get('error', False),
                'ai_enhanced': result.get('ai_enhanced', False)
            })
    
    # Save summary
    summary = {
        'test_date': datetime.now().isoformat(),
        'total_images': len(image_files),
        'images_processed': len(all_results),
        'successful': sum(1 for r in all_results if r['success']),
        'failed': sum(1 for r in all_results if not r['success']),
        'ai_enhanced_count': sum(1 for r in all_results if r.get('ai_enhanced', False)),
        'results': all_results,
        'services': {
            'ocr_service': OCR_SERVICE_URL,
            'ai_service': AI_SERVICE_URL
        }
    }
    
    summary_file = os.path.join(RESULTS_DIR, f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total images: {summary['total_images']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"AI Enhanced: {summary['ai_enhanced_count']}")
    print(f"\nSummary saved to: {os.path.basename(summary_file)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
