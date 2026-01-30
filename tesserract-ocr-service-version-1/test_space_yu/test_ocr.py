#!/usr/bin/env python3
"""
Test script for OCR API with AI Enhancement
Flows: OCR Service (raw text) -> AI LLM Service (enhancement via Ollama)
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time

# API endpoints
OCR_API_URL = "http://localhost:8000"
AI_API_URL = "http://localhost:8004"  # Ollama-based AI service

# Test image path
IMAGE_PATH = Path(__file__).parent.parent / "images_for_Test_yu" / "image2.png"
# IMAGE_PATH = Path("images_for_Test") / "image2.png"

# Output directory for results
OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def enhance_ocr_with_ai(ocr_text: str, language: str = "en") -> dict:
    """
    Send OCR text to AI LLM Service (Ollama) for enhancement and correction.
    
    Args:
        ocr_text: Raw OCR text
        language: Language code (en, km, fr)
        
    Returns:
        Enhanced result from AI service
    """
    print(f"\n4. Enhancing OCR text with AI LLM Service (Ollama)...")
    try:
        # Check AI service health first
        try:
            health_response = requests.get(f"{AI_API_URL}/health", timeout=5)
            if health_response.status_code != 200:
                print(f"⚠️  AI service health check failed: {health_response.status_code}")
        except Exception as e:
            print(f"⚠️  AI service not responding: {e}")
        
        # Send to AI service for correction/enhancement using the /api/v1/chat endpoint
        ai_payload = {
            "message": f"Correct and enhance this OCR text in {language} language. Fix OCR errors, improve formatting, and return clean text:\n\n{ocr_text}",
            "language": language
        }
        
        print(f"📤 Sending text to AI service for enhancement...")
        response = requests.post(f"{AI_API_URL}/api/v1/chat", json=ai_payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Enhancement successful!")
            print(f"\nEnhanced Response:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"⚠️  AI Enhancement failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"⚠️  AI Enhancement request failed: {e}")
        return None

def test_ocr():
    """Test the OCR endpoint with an image and AI enhancement."""
    print(f"Testing OCR API at {OCR_API_URL}")
    print(f"Testing AI LLM Service (Ollama) at {AI_API_URL}")
    print(f"Using image: {IMAGE_PATH}")
    
    if not IMAGE_PATH.exists():
        print(f"❌ Image not found: {IMAGE_PATH}")
        return
    
    # Test 1: Health check
    print("\n1. Testing OCR health endpoint...")
    try:
        response = requests.get(f"{OCR_API_URL}/health", timeout=5)
        print(f"✅ OCR Health check: {response.json()}")
    except Exception as e:
        print(f"❌ OCR Health check failed: {e}")
        return
    
    # Test 2: Get supported languages
    print("\n2. Testing supported languages...")
    try:
        response = requests.get(f"{OCR_API_URL}/languages", timeout=5)
        print(f"✅ Languages: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Languages request failed: {e}")
    
    # Test 3: Process image with OCR
    print("\n3. Testing OCR on image...")
    ocr_result = None
    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": ("image.png", f, "image/png")}
            data = {
                "use_ai_correction": False,  # Skip OCR service's AI, we'll use ours
                "lenient_quality": False,
                "languages": "eng+khm+fra"
            }
            response = requests.post(f"{OCR_API_URL}/ocr", files=files, data=data, timeout=60)
            
        if response.status_code == 200:
            ocr_result = response.json()
            print(f"✅ OCR Processing successful!")
            print(f"\nRaw OCR Result (first 500 chars):")
            full_text = ocr_result.get("full_text", "")
            print(json.dumps({
                "success": ocr_result.get("success"),
                "languages": ocr_result.get("languages"),
                "full_text_preview": full_text[:500] + "..." if len(full_text) > 500 else full_text,
                "overall_confidence": ocr_result.get("overall_confidence")
            }, indent=2))
            
            # Save raw OCR result to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_output_file = OUTPUT_DIR / f"ocr_result_{timestamp}.json"
            
            with open(raw_output_file, "w", encoding="utf-8") as f:
                json.dump(ocr_result, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Raw OCR result saved to: {raw_output_file}")
            
            # Test 4: Enhance with AI if OCR was successful
            if ocr_result and ocr_result.get("full_text"):
                text_to_enhance = ocr_result["full_text"]
                detected_lang = ocr_result.get("languages", ["en"])[0] if ocr_result.get("languages") else "en"
                
                enhanced_result = enhance_ocr_with_ai(
                    ocr_text=text_to_enhance,
                    language=detected_lang
                )
                
                if enhanced_result:
                    # Create combined result with AI enhancement
                    combined_result = {
                        "raw_ocr": {
                            "success": ocr_result.get("success"),
                            "languages": ocr_result.get("languages"),
                            "full_text": ocr_result.get("full_text"),
                            "overall_confidence": ocr_result.get("overall_confidence"),
                            "text_blocks_count": len(ocr_result.get("text_blocks", []))
                        },
                        "ai_enhanced": enhanced_result,
                        "processing_timestamp": timestamp
                    }
                    
                    # Save enhanced result with special naming
                    enhanced_output_file = OUTPUT_DIR / f"ocr_result_ai+enhance_{timestamp}.json"
                    
                    with open(enhanced_output_file, "w", encoding="utf-8") as f:
                        json.dump(combined_result, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n✅ AI+Enhanced result saved to: {enhanced_output_file}")
                else:
                    print(f"\n⚠️  AI enhancement did not return results, only raw OCR saved")
            else:
                print(f"\n⚠️  No full_text in OCR result to enhance")
        else:
            print(f"❌ OCR failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ OCR request failed: {e}")


if __name__ == "__main__":
    test_ocr()
