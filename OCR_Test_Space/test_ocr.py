#!/usr/bin/env python3
"""
OCR Test Script
Tests the OCR service with images from the images/ folder
Saves results as tesseract_result_{N}.json
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime


# Configuration
OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://localhost:8002")
IMAGES_DIR = Path(__file__).parent / "images"
RESULTS_DIR = Path(__file__).parent / "results"

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def get_next_result_number() -> int:
    """Get the next result number"""
    existing = list(RESULTS_DIR.glob("tesseract_result_*.json"))
    if not existing:
        return 1
    
    numbers = []
    for f in existing:
        try:
            num = int(f.stem.split("_")[-1])
            numbers.append(num)
        except ValueError:
            continue
    
    return max(numbers) + 1 if numbers else 1


def test_health():
    """Test the OCR service health endpoint"""
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ OCR Service is {data.get('status', 'unknown')}")
            print(f"  Tesseract installed: {data.get('tesseract', False)}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to OCR service at {OCR_SERVICE_URL}")
        print("  Please start the OCR service first:")
        print("  cd ocr-service && source venv/bin/activate && uvicorn app.main:app --port 8002")
        return False


def test_languages():
    """Check available OCR languages"""
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/api/v1/ocr/languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📚 Available languages: {data.get('available', [])}")
            missing = data.get('missing', [])
            if missing:
                print(f"⚠ Missing required languages: {missing}")
                print("  Install with: sudo apt install tesseract-ocr-khm tesseract-ocr-fra tesseract-ocr-eng")
            else:
                print("✓ All required languages installed (eng, fra, khm)")
            return len(missing) == 0
    except Exception as e:
        print(f"✗ Failed to check languages: {e}")
        return False


def process_image(image_path: Path, result_number: int) -> dict:
    """
    Process a single image through the OCR service
    
    Args:
        image_path: Path to image file
        result_number: Result file number
        
    Returns:
        OCR result dictionary
    """
    print(f"\n📷 Processing: {image_path.name}")
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/jpeg")}
            data = {
                "apply_preprocessing": "true",
                "languages": "khm+eng+fra",
                "include_low_confidence": "true",
                "include_stats": "true"
            }
            
            response = requests.post(
                f"{OCR_SERVICE_URL}/api/v1/ocr/extract",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                # Add metadata
                result["source_file"] = image_path.name
                result["timestamp"] = datetime.now().isoformat()
                result["test_number"] = result_number
                
                # Save result
                output_path = RESULTS_DIR / f"tesseract_result_{result_number}.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                stats = result.get("stats", {})
                print(f"  ✓ Extracted {stats.get('total_words', 0)} words")
                print(f"  ✓ Average confidence: {stats.get('avg_confidence', 0)}%")
                print(f"  ✓ Saved to: {output_path.name}")
                
                return result
            else:
                print(f"  ✗ OCR failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"  ✗ Request failed: {response.status_code}")
            print(f"    {response.text}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error processing image: {e}")
        return None


def main():
    """Main test function"""
    print("=" * 60)
    print("OCR Service Test")
    print("=" * 60)
    
    # Create directories if needed
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test service health
    if not test_health():
        sys.exit(1)
    
    # Check languages
    test_languages()
    
    # Find images
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(IMAGES_DIR.glob(f"*{ext}"))
        images.extend(IMAGES_DIR.glob(f"*{ext.upper()}"))
    
    images = sorted(set(images))
    
    if not images:
        print(f"\n⚠ No images found in {IMAGES_DIR}")
        print("  Please add some test images (.jpg, .png) to the images/ folder")
        print("\n  Example:")
        print(f"    cp /path/to/prescription.jpg {IMAGES_DIR}/")
        sys.exit(0)
    
    print(f"\n📁 Found {len(images)} image(s) to process")
    
    # Process each image
    result_num = get_next_result_number()
    successful = 0
    failed = 0
    
    for image_path in images:
        result = process_image(image_path, result_num)
        if result:
            successful += 1
            result_num += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  ✓ Successful: {successful}")
    print(f"  ✗ Failed: {failed}")
    print(f"  📁 Results saved in: {RESULTS_DIR}")
    
    if successful > 0:
        print("\n  Next step: Use the AI/LLM service to process these results")
        print("  The raw OCR output is in the results/*.json files")


if __name__ == "__main__":
    main()
