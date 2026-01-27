#!/usr/bin/env python3
"""
Comprehensive OCR Testing Script
Tests all images with both RAW PaddleOCR and AI-Enhanced endpoints
Saves results as: result_noAI_<timestamp>.json and result_ai_<timestamp>.json
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
TEST_IMAGES_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/Images_for_test")
RESULTS_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/result_test")
OCR_SERVICE_URL = "http://localhost:8001"  # Updated to port 8001
TIMEOUT = 60  # seconds

# Ensure results directory exists
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def get_timestamp():
    """Generate timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def test_ocr_endpoint(image_path, endpoint, endpoint_name):
    """Test a single image against an OCR endpoint"""
    print(f"\n  Testing: {endpoint_name}")
    print(f"  Image: {image_path.name}")
    print(f"  Endpoint: {endpoint}")
    
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(
                f"{OCR_SERVICE_URL}{endpoint}",
                files={'file': f},
                timeout=TIMEOUT
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ SUCCESS (Status {response.status_code})")
            print(f"  ✓ Returned {len(result.get('text_blocks', []))} text blocks")
            return {
                'status': 'success',
                'status_code': response.status_code,
                'text_blocks_count': len(result.get('text_blocks', [])),
                'data': result
            }
        else:
            print(f"  ✗ FAILED (Status {response.status_code})")
            print(f"  Response: {response.text[:200]}...")
            return {
                'status': 'failed',
                'status_code': response.status_code,
                'error': response.text
            }
    
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}: {str(e)[:100]}")
        return {
            'status': 'error',
            'error': f"{type(e).__name__}: {str(e)}"
        }

def main():
    """Main test execution"""
    print("=" * 80)
    print("COMPREHENSIVE OCR TESTING - Real Images")
    print("=" * 80)
    
    # Get all test images
    image_files = sorted(TEST_IMAGES_DIR.glob("*.png")) + sorted(TEST_IMAGES_DIR.glob("*.jpg"))
    
    if not image_files:
        print(f"\n✗ No test images found in: {TEST_IMAGES_DIR}")
        return
    
    print(f"\n✓ Found {len(image_files)} test images:")
    for img in image_files:
        size_mb = img.stat().st_size / (1024 * 1024)
        print(f"  - {img.name} ({size_mb:.2f} MB)")
    
    timestamp = get_timestamp()
    
    # Results containers
    raw_ocr_results = {
        'timestamp': timestamp,
        'service_url': OCR_SERVICE_URL,
        'endpoint': '/ocr/simple',
        'description': 'Raw PaddleOCR without AI enhancement',
        'images': []
    }
    
    ai_ocr_results = {
        'timestamp': timestamp,
        'service_url': OCR_SERVICE_URL,
        'endpoint': '/ocr',
        'description': 'PaddleOCR with AI LLM enhancement',
        'images': []
    }
    
    # Test each image
    total_images = len(image_files)
    for idx, image_path in enumerate(image_files, 1):
        print(f"\n{'-' * 80}")
        print(f"Image {idx}/{total_images}: {image_path.name}")
        print(f"{'-' * 80}")
        
        image_result_raw = {
            'filename': image_path.name,
            'filepath': str(image_path)
        }
        
        image_result_ai = {
            'filename': image_path.name,
            'filepath': str(image_path)
        }
        
        # Test raw OCR
        print("\n  [1] Raw PaddleOCR (no AI)")
        raw_result = test_ocr_endpoint(image_path, '/ocr/simple', 'Raw PaddleOCR')
        image_result_raw.update(raw_result)
        raw_ocr_results['images'].append(image_result_raw)
        
        # Small delay between requests
        time.sleep(1)
        
        # Test AI-enhanced OCR
        print("\n  [2] AI-Enhanced OCR")
        ai_result = test_ocr_endpoint(image_path, '/ocr', 'AI-Enhanced OCR')
        image_result_ai.update(ai_result)
        ai_ocr_results['images'].append(image_result_ai)
        
        time.sleep(1)
    
    # Save results
    print(f"\n{'=' * 80}")
    print("SAVING RESULTS")
    print(f"{'=' * 80}")
    
    # Raw OCR results file
    raw_filename = f"result_noAI_{timestamp}.json"
    raw_filepath = RESULTS_DIR / raw_filename
    with open(raw_filepath, 'w') as f:
        json.dump(raw_ocr_results, f, indent=2)
    print(f"\n✓ Raw OCR results saved: {raw_filepath}")
    print(f"  File size: {raw_filepath.stat().st_size / 1024:.2f} KB")
    
    # AI-enhanced results file
    ai_filename = f"result_ai_{timestamp}.json"
    ai_filepath = RESULTS_DIR / ai_filename
    with open(ai_filepath, 'w') as f:
        json.dump(ai_ocr_results, f, indent=2)
    print(f"\n✓ AI-enhanced OCR results saved: {ai_filepath}")
    print(f"  File size: {ai_filepath.stat().st_size / 1024:.2f} KB")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    
    raw_success = sum(1 for img in raw_ocr_results['images'] if img.get('status') == 'success')
    ai_success = sum(1 for img in ai_ocr_results['images'] if img.get('status') == 'success')
    
    print(f"\nRaw PaddleOCR: {raw_success}/{total_images} successful")
    print(f"AI-Enhanced OCR: {ai_success}/{total_images} successful")
    
    print(f"\nResults files:")
    print(f"  Raw OCR: {raw_filename}")
    print(f"  AI OCR:  {ai_filename}")
    
    print(f"\n{'=' * 80}")
    if raw_success > 0 and ai_success > 0:
        print("✓ TEST COMPLETED SUCCESSFULLY!")
    else:
        print("⚠ TEST COMPLETED WITH ISSUES - Check error details above")
    print(f"{'=' * 80}\n")

if __name__ == '__main__':
    main()
