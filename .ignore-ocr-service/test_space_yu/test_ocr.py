#!/usr/bin/env python3
"""
Test script for OCR API
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# API endpoint
API_URL = "http://localhost:8000"

# Test image path
IMAGE_PATH = Path(__file__).parent.parent / "images_for_Test_yu" / "image2.png"
# IMAGE_PATH = Path("images_for_Test") / "image2.png"

# Output directory for results
OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_ocr():
    """Test the OCR endpoint with an image."""
    print(f"Testing OCR API at {API_URL}")
    print(f"Using image: {IMAGE_PATH}")
    
    if not IMAGE_PATH.exists():
        print(f"❌ Image not found: {IMAGE_PATH}")
        return
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"✅ Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Get supported languages
    print("\n2. Testing supported languages...")
    try:
        response = requests.get(f"{API_URL}/languages")
        print(f"✅ Languages: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Languages request failed: {e}")
    
    # Test 3: Process image with OCR
    print("\n3. Testing OCR on image...")
    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": ("image.png", f, "image/png")}
            data = {
                "use_ai_correction": True,
                "lenient_quality": False,
                "languages": "eng+khm+fra"
            }
            response = requests.post(f"{API_URL}/ocr", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OCR Processing successful!")
            print(f"\nResult:")
            print(json.dumps(result, indent=2))
            
            # Save result to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"ocr_result_{timestamp}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Result saved to: {output_file}")
        else:
            print(f"❌ OCR failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ OCR request failed: {e}")

if __name__ == "__main__":
    test_ocr()
