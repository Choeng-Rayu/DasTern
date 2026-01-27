"""
Test OCR with and without AI enhancement
Compare PaddleOCR raw results vs AI-enhanced results
"""
import requests
import json
from datetime import datetime
import time

SERVICE_URL = "http://localhost:8000"
TEST_IMAGE = "/home/rayu/DasTern/OCR_Test_Space/Images_for_test/image.png"

def test_ocr_comparison():
    """Test OCR with and without AI enhancement"""
    print(f"\n{'='*70}")
    print(f"OCR COMPARISON TEST: AI-Enhanced vs Raw PaddleOCR")
    print(f"Image: {TEST_IMAGE}")
    print(f"{'='*70}\n")
    
    # Test 1: OCR without AI (simple endpoint)
    print("1. Testing RAW PaddleOCR (NO AI Enhancement)...")
    print("-" * 70)
    
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": ("test.png", f, "image/png")}
        response_noai = requests.post(f"{SERVICE_URL}/ocr/simple", files=files)
    
    if response_noai.status_code != 200:
        print(f"❌ Error (No AI): {response_noai.status_code}")
        print(response_noai.text)
        return
    
    result_noai = response_noai.json()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw OCR result
    output_noai = f"result_noAI_{timestamp}.json"
    with open(output_noai, "w", encoding="utf-8") as f:
        json.dump(result_noai, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Raw PaddleOCR completed")
    print(f"  Saved to: {output_noai}")
    
    blocks_noai = result_noai.get("raw_blocks", [])
    print(f"  Total blocks: {len(blocks_noai)}")
    if blocks_noai:
        avg_conf = sum(b.get("confidence", 0) for b in blocks_noai) / len(blocks_noai)
        print(f"  Average confidence: {avg_conf:.2%}")
    print()
    
    # Wait a bit before next request
    time.sleep(2)
    
    # Test 2: OCR with AI enhancement
    print("2. Testing AI-ENHANCED OCR...")
    print("-" * 70)
    
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": ("test.png", f, "image/png")}
        response_ai = requests.post(f"{SERVICE_URL}/ocr", files=files)
    
    if response_ai.status_code != 200:
        print(f"❌ Error (AI Enhanced): {response_ai.status_code}")
        print(response_ai.text)
        return
    
    result_ai = response_ai.json()
    
    # Save AI-enhanced result
    output_ai = f"result_ai_{timestamp}.json"
    with open(output_ai, "w", encoding="utf-8") as f:
        json.dump(result_ai, f, ensure_ascii=False, indent=2)
    
    print(f"✓ AI-Enhanced OCR completed")
    print(f"  Saved to: {output_ai}")
    
    ai_enhanced = result_ai.get("ai_enhanced", False)
    print(f"  AI Enhancement: {'Yes' if ai_enhanced else 'No/Failed'}")
    
    structured = result_ai.get("structured_data", {})
    if structured:
        print(f"  Structured data extracted: Yes")
        if "patient" in structured:
            print(f"    - Patient info: {structured['patient']}")
        if "medications" in structured:
            print(f"    - Medications: {len(structured['medications'])} items")
    print()
    
    # Comparison
    print(f"\n{'='*70}")
    print(f"COMPARISON SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n📊 Raw PaddleOCR (No AI):")
    print(f"   File: {output_noai}")
    print(f"   Blocks: {len(blocks_noai)}")
    if blocks_noai:
        langs_noai = {}
        for b in blocks_noai:
            lang = b.get("language", "unknown")
            langs_noai[lang] = langs_noai.get(lang, 0) + 1
        print(f"   Languages: {langs_noai}")
    
    print(f"\n🤖 AI-Enhanced OCR:")
    print(f"   File: {output_ai}")
    print(f"   AI Status: {'Enhanced' if ai_enhanced else 'Not Available'}")
    print(f"   Structured: {'Yes' if structured else 'No'}")
    
    # Show text samples
    print(f"\n{'='*70}")
    print(f"TEXT SAMPLES (First 10 blocks - Raw PaddleOCR)")
    print(f"{'='*70}")
    for i, block in enumerate(blocks_noai[:10], 1):
        text = block.get("text", "")
        conf = block.get("confidence", 0)
        lang = block.get("language", "?")
        print(f"{i}. [{lang}] [{conf:.1%}] {text}")
    
    print(f"\n{'='*70}")
    print(f"✅ COMPARISON TEST COMPLETE!")
    print(f"{'='*70}\n")
    print(f"Results:")
    print(f"  - Raw PaddleOCR: {output_noai}")
    print(f"  - AI Enhanced:   {output_ai}")
    print()

if __name__ == "__main__":
    test_ocr_comparison()
