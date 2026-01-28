#!/usr/bin/env python3
"""
Comprehensive OCR Test Script
Tests prescription OCR accuracy and functionality
"""

import requests
import json
import os
from datetime import datetime

# Service URLs
OCR_URL = "http://localhost:8001/ocr"
AI_URL = "http://localhost:8002"

def test_image(image_path):
    """Test OCR on a single image"""
    print(f"\n=== Testing: {os.path.basename(image_path)} ===")
    
    # Test OCR
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(OCR_URL, files=files)
            
        if response.status_code == 200:
            result = response.json()
            print(f"✓ OCR Success: {result.get('success', False)}")
            print(f"✓ Blocks extracted: {len(result.get('blocks', []))}")
            print(f"✓ Overall confidence: {result.get('overall_confidence', 0):.3f}")
            print(f"✓ Primary language: {result.get('primary_language', 'unknown')}")
            print(f"✓ AI Enhanced: {result.get('ai_enhanced', False)}")
            
            # Show first few text blocks
            blocks = result.get('blocks', [])
            print(f"\nFirst 10 text blocks:")
            for i, block in enumerate(blocks[:10]):
                text = block.get('text', '')
                conf = block.get('confidence', 0)
                lang = block.get('language', '?')
                if text.strip():
                    print(f"  {i+1:2d}: [{lang}] {text:20s} (conf: {conf:.2f})")
            
            # Check for Khmer text
            khmer_blocks = [b for b in blocks if b.get('language') == 'kh']
            english_blocks = [b for b in blocks if b.get('language') == 'en']
            print(f"\nLanguage breakdown:")
            print(f"  Khmer: {len(khmer_blocks)} blocks")
            print(f"  English: {len(english_blocks)} blocks")
            print(f"  Other: {len(blocks) - len(khmer_blocks) - len(english_blocks)} blocks")
            
            # Check for medical terms
            medical_keywords = ['ឱស', 'medicine', 'ថ្នាំ', 'doctor', 'គ្រូង', 'prescription']
            text_content = ' '.join([b.get('text', '') for b in blocks])
            found_medical = [kw for kw in medical_keywords if kw.lower() in text_content.lower()]
            if found_medical:
                print(f"✓ Medical keywords detected: {found_medical}")
            
            return result
            
        else:
            print(f"✗ OCR failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error testing image: {e}")
        return None

def test_services():
    """Test service health"""
    print("=== Service Health Check ===")
    
    # Test OCR service
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✓ OCR Service: Healthy")
        else:
            print("✗ OCR Service: Unhealthy")
    except:
        print("✗ OCR Service: Not responding")
    
    # Test AI service
    try:
        response = requests.get(f"{AI_URL}/")
        if response.status_code == 200:
            print("✓ AI Service: Healthy")
        else:
            print("✗ AI Service: Unhealthy")
    except:
        print("✗ AI Service: Not responding")

def main():
    """Run comprehensive OCR tests"""
    print("DasTern OCR System Test")
    print("=" * 50)
    
    # Test services first
    test_services()
    
    # Test all prescription images
    test_images = [
        "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image.png",
        "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image1.png", 
        "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image2.png"
    ]
    
    results = []
    for img_path in test_images:
        if os.path.exists(img_path):
            result = test_image(img_path)
            if result:
                results.append({
                    'image': os.path.basename(img_path),
                    'success': result.get('success', False),
                    'blocks': len(result.get('blocks', [])),
                    'confidence': result.get('overall_confidence', 0),
                    'language': result.get('primary_language', 'unknown'),
                    'ai_enhanced': result.get('ai_enhanced', False)
                })
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total_images = len(results)
    successful = sum(1 for r in results if r['success'])
    total_blocks = sum(r['blocks'] for r in results)
    avg_confidence = sum(r['confidence'] for r in results) / total_images if total_images > 0 else 0
    
    print(f"Total images tested: {total_images}")
    print(f"Successful OCR: {successful}/{total_images}")
    print(f"Total text blocks: {total_blocks}")
    print(f"Average confidence: {avg_confidence:.3f}")
    
    print(f"\nDetailed results:")
    for r in results:
        status = "✓" if r['success'] else "✗"
        print(f"  {status} {r['image']:15s} | {r['blocks']:3d} blocks | {r['confidence']:.3f} conf | {r['language']:5s} | AI:{r['ai_enhanced']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/home/rayu/DasTern/OCR_Test_Space/result_test/ocr_test_summary_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'test_summary': {
                'total_images': total_images,
                'successful': successful,
                'total_blocks': total_blocks,
                'average_confidence': avg_confidence
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()