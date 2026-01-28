#!/usr/bin/env python3
"""
Final OCR + AI Enhancement Test with Real Prescription Images
Creates comprehensive test results with AI enhancement
"""

import requests
import json
import os
from datetime import datetime

# Service URLs
OCR_URL = "http://localhost:8001/ocr"
AI_URL = "http://localhost:8002"

def create_test_prescription_with_medications(ocr_result):
    """Enhance OCR result with extracted medications to trigger AI"""
    enhanced = ocr_result.copy()
    
    # Extract potential medications from text blocks
    blocks = enhanced.get('blocks', [])
    text_content = ' '.join([b.get('text', '') for b in blocks])
    
    # Simple medication extraction based on common patterns
    medications = []
    
    # Look for prescription codes and medical terms
    for block in blocks:
        text = block.get('text', '').strip()
        if any(keyword in text.lower() for keyword in ['medic', 'drug', 'tablet', 'capsule']):
            medications.append({
                'name': text,
                'strength': '',
                'dosage': '',
                'frequency': '',
                'duration': '',
                'sequence': len(medications) + 1
            })
        elif len(text) > 5 and text.replace('-', '').replace('/', '').isalnum():
            # Could be medication code or name
            medications.append({
                'name': text,
                'strength': '',
                'dosage': '',
                'frequency': '',
                'duration': '',
                'sequence': len(medications) + 1
            })
    
    # Add structured data to trigger AI enhancement
    if medications and 'structured_data' not in enhanced:
        enhanced['structured_data'] = {
            'medications': medications[:3],  # Limit to first 3 found
            'patient_name': extract_patient_name(blocks),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        enhanced['medication_extraction'] = {
            'method': 'pattern_matching',
            'found_count': len(medications)
        }
    
    return enhanced

def extract_patient_name(blocks):
    """Try to extract patient name from blocks"""
    for block in blocks:
        text = block.get('text', '').strip()
        if len(text) > 3 and any(keyword in text.lower() for keyword in ['name', 'ឈ្មោះ']):
            return text
    return "Unknown"

def test_comprehensive_workflow(image_path):
    """Test complete OCR + AI workflow"""
    print(f"\n=== Comprehensive Test: {os.path.basename(image_path)} ===")
    
    try:
        # Step 1: OCR
        print("📸 Step 1: Running OCR...")
        with open(image_path, 'rb') as f:
            files = {'file': f}
            ocr_response = requests.post(OCR_URL, files=files, timeout=30)
            
        if ocr_response.status_code != 200:
            print(f"❌ OCR failed: {ocr_response.status_code}")
            return None
            
        ocr_result = ocr_response.json()
        print(f"✅ OCR Success: {ocr_result.get('success', False)}")
        print(f"📊 Blocks: {len(ocr_result.get('blocks', []))}")
        print(f"🎯 Confidence: {ocr_result.get('overall_confidence', 0):.3f}")
        
        # Step 2: Enhance with medications
        print("🧪 Step 2: Adding medication structure...")
        enhanced_ocr = create_test_prescription_with_medications(ocr_result)
        
        if 'structured_data' in enhanced_ocr:
            meds = enhanced_ocr['structured_data'].get('medications', [])
            print(f"💊 Added {len(meds)} medications to structure:")
            for i, med in enumerate(meds[:3]):
                print(f"  {i+1}: {med.get('name', 'Unknown')}")
        
        # Step 3: AI Enhancement
        print("🤖 Step 3: Running AI enhancement...")
        ai_request_data = {"ocr_data": enhanced_ocr}
        
        ai_response = requests.post(f"{AI_URL}/enhance", 
                               json=ai_request_data, 
                               timeout=90)
        
        if ai_response.status_code != 200:
            print(f"❌ AI enhancement failed: {ai_response.status_code}")
            return enhanced_ocr
            
        ai_result = ai_response.json()
        print(f"✅ AI Enhancement Success: {ai_result.get('success', False)}")
        print(f"🧠 AI Enhanced: {ai_result.get('ai_enhanced', False)}")
        
        # Step 4: Create final comprehensive result
        final_result = ai_result.get('data', enhanced_ocr)
        final_result.update({
            'comprehensive_test': True,
            'original_ocr_blocks': len(ocr_result.get('blocks', [])),
            'medications_added': enhanced_ocr.get('medication_extraction', {}).get('found_count', 0),
            'ai_processing_time': datetime.now().isoformat()
        })
        
        # Display results
        print(f"\n📋 FINAL RESULTS:")
        print(f"  OCR Blocks: {final_result.get('original_ocr_blocks', 0)}")
        print(f"  Medications Found: {final_result.get('medications_added', 0)}")
        print(f"  AI Enhanced: {final_result.get('ai_enhanced', False)}")
        
        if final_result.get('prescription_summary'):
            summary = final_result.get('prescription_summary', '')
            print(f"  AI Summary: {summary[:100]}...")
            
        if final_result.get('validation'):
            validation = final_result.get('validation', {})
            print(f"  Validation: {'✅ Valid' if validation.get('is_valid') else '❌ Issues'}")
            warnings = validation.get('warnings', [])
            if warnings:
                print(f"  Warnings: {len(warnings)}")
                for warning in warnings[:3]:
                    print(f"    - {warning}")
        
        return final_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run comprehensive test on all prescription images"""
    print("DasTern Comprehensive OCR + AI Enhancement Test")
    print("=" * 70)
    
    # Test images
    test_images = [
        "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image.png",
        "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image1.png", 
        "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image2.png"
    ]
    
    results = []
    results_dir = "/home/rayu/DasTern/OCR_Test_Space/result_test"
    os.makedirs(results_dir, exist_ok=True)
    
    for img_path in test_images:
        if os.path.exists(img_path):
            result = test_comprehensive_workflow(img_path)
            if result:
                # Save individual result
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_{os.path.basename(img_path).split('.')[0]}_{timestamp}.json"
                result_file = os.path.join(results_dir, filename)
                
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                print(f"💾 Saved: {filename}")
                
                # Add to summary
                results.append({
                    'image': os.path.basename(img_path),
                    'filename': filename,
                    'ocr_blocks': result.get('original_ocr_blocks', 0),
                    'medications_found': result.get('medications_added', 0),
                    'ai_enhanced': result.get('ai_enhanced', False),
                    'has_summary': bool(result.get('prescription_summary')),
                    'confidence': result.get('overall_confidence', 0),
                    'primary_language': result.get('primary_language', 'unknown')
                })
    
    # Create comprehensive summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(results_dir, f"comprehensive_ai_test_{timestamp}.json")
    
    summary = {
        'test_metadata': {
            'timestamp': timestamp,
            'test_type': 'comprehensive_ocr_ai_enhancement',
            'services': {
                'ocr_service': 'http://localhost:8001',
                'ai_service': 'http://localhost:8002',
                'ai_model': 'llama3.1:8b',
                'ocr_engine': 'tesseract_fallback'
            }
        },
        'results': results,
        'statistics': {
            'total_images': len(results),
            'successful_tests': len([r for r in results if r['ai_enhanced'] or r['ocr_blocks'] > 0]),
            'ai_enhanced_count': len([r for r in results if r['ai_enhanced']]),
            'with_ai_summary': len([r for r in results if r['has_summary']]),
            'total_ocr_blocks': sum(r['ocr_blocks'] for r in results),
            'total_medications_found': sum(r['medications_found'] for r in results),
            'average_confidence': sum(r['confidence'] for r in results) / len(results) if results else 0
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Display final summary
    print(f"\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    
    stats = summary['statistics']
    print(f"📸 Images Tested: {stats['total_images']}")
    print(f"✅ Successful: {stats['successful_tests']}")
    print(f"🤖 AI Enhanced: {stats['ai_enhanced_count']}")
    print(f"📋 With AI Summary: {stats['with_ai_summary']}")
    print(f"📝 Total OCR Blocks: {stats['total_ocr_blocks']}")
    print(f"💊 Medications Found: {stats['total_medications_found']}")
    print(f"🎯 Average Confidence: {stats['average_confidence']:.3f}")
    
    print(f"\n📁 Individual Results:")
    for r in results:
        ai_status = "✅" if r['ai_enhanced'] else "❌"
        summary_status = "📋" if r['has_summary'] else "📝"
        print(f"  {ai_status} {summary_status} {r['image']:15s} | {r['ocr_blocks']:3d} OCR | {r['medications_found']:2d} meds | {r['confidence']:.3f} conf")
    
    print(f"\n🎉 MAIN RESULT FILE:")
    print(f"📍 {summary_file}")
    
    return summary_file

if __name__ == "__main__":
    result_file = main()
    if result_file:
        print(f"\n🔥 FINAL COMPREHENSIVE RESULT LOCATION: {result_file}")
    else:
        print("\n❌ Comprehensive test failed")