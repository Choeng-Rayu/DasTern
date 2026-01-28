#!/usr/bin/env python3
"""
Comprehensive OCR + AI Enhancement Test
Tests complete workflow with AI enhancement and saves results
"""

import requests
import json
import os
from datetime import datetime

# Service URLs
OCR_URL = "http://localhost:8001/ocr"
AI_URL = "http://localhost:8002"

def test_image_with_ai(image_path, result_file):
    """Test OCR with AI enhancement on a single image"""
    print(f"\n=== Testing: {os.path.basename(image_path)} ===")
    
    try:
        # Step 1: Run OCR
        print("Step 1: Running OCR...")
        with open(image_path, 'rb') as f:
            files = {'file': f}
            ocr_response = requests.post(OCR_URL, files=files)
            
        if ocr_response.status_code != 200:
            print(f"✗ OCR failed with status {ocr_response.status_code}")
            return None
            
        ocr_result = ocr_response.json()
        print(f"✓ OCR Success: {ocr_result.get('success', False)}")
        print(f"✓ Blocks extracted: {len(ocr_result.get('blocks', []))}")
        print(f"✓ AI Enhanced: {ocr_result.get('ai_enhanced', False)}")
        
        # Step 2: Manual AI enhancement (to ensure it runs)
        print("Step 2: Running AI enhancement...")
        
        # Prepare data for AI service
        ai_request_data = {
            "ocr_data": ocr_result
        }
        
        try:
            ai_response = requests.post(f"{AI_URL}/enhance", 
                                   json=ai_request_data, 
                                   timeout=60)  # Longer timeout for AI processing
            
            if ai_response.status_code == 200:
                ai_result = ai_response.json()
                print(f"✓ AI Enhancement Success: {ai_result.get('success', False)}")
                print(f"✓ AI Enhanced: {ai_result.get('ai_enhanced', False)}")
                
                # Merge AI results into OCR result
                enhanced_result = ocr_result.copy()
                enhanced_result.update({
                    'ai_enhanced': ai_result.get('ai_enhanced', False),
                    'prescription_summary': ai_result.get('prescription_summary'),
                    'validation': ai_result.get('validation'),
                    'ai_processing': {
                        'success': ai_result.get('success', False),
                        'ai_enhanced': ai_result.get('ai_enhanced', False),
                        'timestamp': datetime.now().isoformat()
                    }
                })
                
                # Step 3: Analyze and display results
                print(f"\n=== ENHANCED RESULTS ===")
                
                # Show text blocks with better formatting
                blocks = enhanced_result.get('blocks', [])
                print(f"Total text blocks: {len(blocks)}")
                
                # Group by language
                lang_groups = {}
                for block in blocks:
                    lang = block.get('language', 'unknown')
                    if lang not in lang_groups:
                        lang_groups[lang] = []
                    text = block.get('text', '').strip()
                    if text:
                        lang_groups[lang].append(text)
                
                print("\nExtracted text by language:")
                for lang, texts in lang_groups.items():
                    print(f"  [{lang.upper()}] ({len(texts)} blocks):")
                    for i, text in enumerate(texts[:5]):  # Show first 5
                        print(f"    {i+1}: {text}")
                    if len(texts) > 5:
                        print(f"    ... and {len(texts) - 5} more")
                
                # Show AI enhancement if available
                if enhanced_result.get('ai_enhanced'):
                    summary = enhanced_result.get('prescription_summary', '')
                    validation = enhanced_result.get('validation', {})
                    print(f"\n🤖 AI PRESCRIPTION SUMMARY:")
                    print(f"  {summary}")
                    
                    if validation:
                        print(f"\n✅ AI VALIDATION:")
                        print(f"  Is valid: {validation.get('is_valid', False)}")
                        warnings = validation.get('warnings', [])
                        if warnings:
                            print(f"  Warnings: {warnings}")
                else:
                    print(f"\n⚠️  AI enhancement was not applied")
                    ai_processing = enhanced_result.get('ai_processing', {})
                    print(f"  AI processing success: {ai_processing.get('success', False)}")
                
                return enhanced_result
                
            else:
                print(f"✗ AI enhancement failed with status {ai_response.status_code}")
                print(f"AI response: {ai_response.text}")
                return ocr_result  # Return OCR-only result
                
        except requests.exceptions.Timeout:
            print("✗ AI enhancement timed out")
            return ocr_result
        except Exception as e:
            print(f"✗ AI enhancement error: {e}")
            return ocr_result
            
    except Exception as e:
        print(f"✗ Error testing image: {e}")
        return None

def test_all_images():
    """Test all prescription images with AI enhancement"""
    print("DasTern OCR + AI Enhancement Test")
    print("=" * 60)
    
    # Find all test images
    test_dir = "/home/rayu/DasTern/OCR_Test_Space/Images_for_test"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    test_images = [os.path.join(test_dir, f) for f in os.listdir(test_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not test_images:
        print("❌ No test images found")
        return
    
    print(f"Found {len(test_images)} test images")
    
    # Create results directory
    results_dir = "/home/rayu/DasTern/OCR_Test_Space/result_test"
    os.makedirs(results_dir, exist_ok=True)
    
    # Test each image
    all_results = []
    for img_path in sorted(test_images):
        result = test_image_with_ai(img_path, results_dir)
        if result:
            # Save individual result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_enhanced_{os.path.basename(img_path).split('.')[0]}_{timestamp}.json"
            result_file = os.path.join(results_dir, filename)
            
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"💾 Results saved: {result_file}")
            
            # Add to summary
            all_results.append({
                'image': os.path.basename(img_path),
                'result_file': filename,
                'success': result.get('success', False),
                'blocks': len(result.get('blocks', [])),
                'confidence': result.get('overall_confidence', 0),
                'primary_language': result.get('primary_language', 'unknown'),
                'ai_enhanced': result.get('ai_enhanced', False),
                'has_summary': bool(result.get('prescription_summary'))
            })
    
    # Create summary report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(results_dir, f"ai_enhancement_summary_{timestamp}.json")
    
    summary = {
        'timestamp': timestamp,
        'test_info': {
            'total_images': len(all_results),
            'services_used': {
                'ocr_service': 'http://localhost:8001',
                'ai_service': 'http://localhost:8002',
                'ai_model': 'llama3.1:8b'
            }
        },
        'results': all_results,
        'summary_stats': {
            'total_images': len(all_results),
            'successful_ocr': sum(1 for r in all_results if r['success']),
            'ai_enhanced': sum(1 for r in all_results if r['ai_enhanced']),
            'with_summary': sum(1 for r in all_results if r['has_summary']),
            'total_blocks': sum(r['blocks'] for r in all_results),
            'avg_confidence': sum(r['confidence'] for r in all_results) / len(all_results) if all_results else 0
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    stats = summary['summary_stats']
    print(f"📊 Total Images: {stats['successful_ocr']}/{stats['total_images']}")
    print(f"🤖 AI Enhanced: {stats['ai_enhanced']}")
    print(f"📋 With Summary: {stats['with_summary']}")
    print(f"📝 Total Text Blocks: {stats['total_blocks']}")
    print(f"🎯 Average Confidence: {stats['avg_confidence']:.3f}")
    
    print(f"\n📁 Individual Results:")
    for r in all_results:
        ai_status = "✅" if r['ai_enhanced'] else "❌"
        print(f"  {ai_status} {r['image']:20s} | {r['blocks']:3d} blocks | {r['confidence']:.3f} conf | {r['primary_language']}")
    
    print(f"\n🎉 Summary file: {summary_file}")
    return summary_file

if __name__ == "__main__":
    result_file = test_all_images()
    if result_file:
        print(f"\n📍 FINAL RESULT LOCATION: {result_file}")
    else:
        print("\n❌ Test failed - no results generated")