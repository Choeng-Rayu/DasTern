"""
Test OCR service with PaddleOCR - Check if Khmer is recognized
"""
import requests
import json
from datetime import datetime

SERVICE_URL = "http://localhost:8000"
TEST_IMAGE = "/home/rayu/DasTern/.ignore-ocr-service/images_for_Test_yu/image.png"

def test_paddleocr():
    """Test OCR service with PaddleOCR"""
    print(f"\n{'='*60}")
    print(f"Testing PaddleOCR with image: {TEST_IMAGE}")
    print(f"{'='*60}\n")
    
    # Test health
    health = requests.get(f"{SERVICE_URL}/health")
    print(f"✓ Health check: {health.json()['status']}")
    print()
    
    # Process image with /ocr endpoint
    print("Processing image with PaddleOCR...")
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": ("test.png", f, "image/png")}
        response = requests.post(f"{SERVICE_URL}/ocr", files=files)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    
    # Save full result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"paddleocr_test_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ OCR completed successfully")
    print(f"  Results saved to: {output_file}")
    print()
    
    # Analyze results
    blocks = result.get("raw_blocks", [])
    print(f"{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total blocks extracted: {len(blocks)}")
    
    # Count by language
    lang_counts = {}
    for block in blocks:
        lang = block.get("language", "unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    print(f"\nLanguage distribution:")
    for lang, count in sorted(lang_counts.items()):
        print(f"  {lang}: {count} blocks")
    
    # Average confidence
    if blocks:
        avg_conf = sum(b.get("confidence", 0) for b in blocks) / len(blocks)
        print(f"\nAverage confidence: {avg_conf:.2%}")
    
    # Show sample of Khmer blocks
    khmer_blocks = [b for b in blocks if b.get("language") == "kh"]
    if khmer_blocks:
        print(f"\n{'='*60}")
        print(f"KHMER TEXT SAMPLES (first 5):")
        print(f"{'='*60}")
        for i, block in enumerate(khmer_blocks[:5], 1):
            text = block.get("text", "")
            conf = block.get("confidence", 0)
            print(f"{i}. [{conf:.1%}] {text}")
    else:
        print(f"\n⚠ No Khmer text detected")
    
    # Show sample of all blocks
    print(f"\n{'='*60}")
    print(f"ALL TEXT BLOCKS (first 10):")
    print(f"{'='*60}")
    for i, block in enumerate(blocks[:10], 1):
        text = block.get("text", "")
        conf = block.get("confidence", 0)
        lang = block.get("language", "?")
        print(f"{i}. [{lang}] [{conf:.1%}] {text}")
    
    print(f"\n{'='*60}")
    print(f"✓ PaddleOCR test complete!")
    print(f"Full results in: {output_file}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    test_paddleocr()
