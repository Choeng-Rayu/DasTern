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
from typing import Optional


# Configuration
OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://localhost:8002")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
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


def test_ai_service():
    """Test the AI service health"""
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ AI Service is {data.get('status', 'unknown')}")
            return True
        else:
            print(f"✗ AI Service health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to AI service at {AI_SERVICE_URL}")
        return False


def enhance_with_ai(raw_text: str) -> dict:
    """
    Enhance OCR text with AI service for cleaning and reminder conversion
    
    Args:
        raw_text: Raw OCR text
        
    Returns:
        Enhanced text with AI corrections and reminder format
    """
    try:
        # Try to use AI service if available
        correction_payload = {
            "text": raw_text,
            "language": "en"
        }
        
        correction_response = requests.post(
            f"{AI_SERVICE_URL}/correct-ocr",
            json=correction_payload,
            timeout=30
        )
        
        if correction_response.status_code == 200:
            correction_result = correction_response.json()
            corrected_text = correction_result.get("corrected_text", raw_text)
            confidence = correction_result.get("confidence", 0.0)
            print(f"  🤖 AI corrected text (confidence: {confidence:.2f})")
        else:
            print(f"  ⚠ AI correction failed: {correction_response.status_code}")
            corrected_text = raw_text
        
        # Try chat endpoint for reminder conversion
        chat_payload = {
            "message": f"Convert this medical prescription into a clear reminder format: {corrected_text}",
            "language": "en",
            "context": {"task": "reminder_conversion"}
        }
        
        chat_response = requests.post(
            f"{AI_SERVICE_URL}/api/v1/chat",
            json=chat_payload,
            timeout=30
        )
        
        if chat_response.status_code == 200:
            chat_result = chat_response.json()
            reminder_text = chat_result.get("response", corrected_text)
            print(f"  📋 AI converted to reminder format")
        else:
            print(f"  ⚠ AI reminder conversion failed: {chat_response.status_code}")
            reminder_text = corrected_text
        
        return {
            "corrected_text": corrected_text,
            "reminder_text": reminder_text,
            "ai_enhanced": True
        }
        
    except Exception as e:
        print(f"  ✗ AI enhancement failed: {e}")
        # Fallback to simple text cleaning and reminder formatting
        corrected_text = simple_text_cleaning(raw_text)
        reminder_text = create_simple_reminder(corrected_text)
        
        return {
            "corrected_text": corrected_text,
            "reminder_text": reminder_text,
            "ai_enhanced": False,
            "fallback_used": True
        }


def simple_text_cleaning(text: str) -> str:
    """Simple text cleaning as fallback"""
    # Remove extra spaces and fix common OCR errors
    cleaned = ' '.join(text.split())
    
    # Fix common medical OCR mistakes
    corrections = {
        "Parscotamol": "Paracetamol",
        "Tako": "Take",
        "2ibotsdeiy": "2 tablets daily",
        "Morning": "Morning",
        "Evening": "Evening",
        "Duration": "Duration",
        "days": "days"
    }
    
    for wrong, right in corrections.items():
        cleaned = cleaned.replace(wrong, right)
    
    return cleaned


def create_simple_reminder(text: str) -> str:
    """Create simple reminder format from cleaned text"""
    lines = text.split('\n')
    reminder_parts = []
    
    for line in lines:
        if "Take" in line or "Morning" in line or "Evening" in line:
            reminder_parts.append(f"• {line.strip()}")
        elif "Duration" in line:
            reminder_parts.append(f"• {line.strip()}")
    
    if not reminder_parts:
        reminder_parts.append(f"• {text.strip()}")
    
    return "\n".join(reminder_parts)


def process_image(image_path: Path, result_number: int) -> Optional[dict]:
    """
    Process a single image through the OCR service and enhance with AI
    
    Args:
        image_path: Path to image file
        result_number: Result file number
        
    Returns:
        OCR result dictionary with AI enhancements
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
                # Extract raw text for AI enhancement
                raw_text = " ".join([item.get("text", "") for item in result.get("raw", [])])
                
                # Enhance with AI
                ai_enhancement = enhance_with_ai(raw_text)
                
                # Add AI enhancement to result
                result.update(ai_enhancement)
                
                # Add metadata
                result["source_file"] = image_path.name
                result["timestamp"] = datetime.now().isoformat()
                result["test_number"] = result_number
                
                # Save result
                output_path = RESULTS_DIR / f"tesseract_result_{result_number}.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # Also save AI-enhanced version
                ai_output_path = RESULTS_DIR / f"ai_enhanced_result_{result_number}.json"
                ai_result = {
                    "source_file": image_path.name,
                    "timestamp": datetime.now().isoformat(),
                    "test_number": result_number,
                    "raw_text": raw_text,
                    "corrected_text": ai_enhancement.get("corrected_text", ""),
                    "reminder_text": ai_enhancement.get("reminder_text", ""),
                    "ai_enhanced": ai_enhancement.get("ai_enhanced", False)
                }
                with open(ai_output_path, "w", encoding="utf-8") as f:
                    json.dump(ai_result, f, ensure_ascii=False, indent=2)
                
                stats = result.get("stats", {})
                print(f"  ✓ Extracted {stats.get('total_words', 0)} words")
                print(f"  ✓ Average confidence: {stats.get('avg_confidence', 0)}%")
                print(f"  ✓ Saved to: {output_path.name}")
                print(f"  ✓ AI enhanced saved to: {ai_output_path.name}")
                
                # Show AI results
                if ai_enhancement.get("ai_enhanced"):
                    print(f"  📝 Corrected: {ai_enhancement.get('corrected_text', '')[:100]}...")
                    print(f"  📋 Reminder: {ai_enhancement.get('reminder_text', '')[:100]}...")
                
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
    print("OCR + AI Service Test")
    print("=" * 60)
    
    # Create directories if needed
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test OCR service health
    if not test_health():
        sys.exit(1)
    
    # Test AI service health
    if not test_ai_service():
        print("⚠ AI service not available - will skip AI enhancement")
    
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
        print("\n  📝 Raw OCR results: tesseract_result_*.json")
        print("  🤖 AI enhanced results: ai_enhanced_result_*.json")
        print("  📋 Check the AI enhanced files for cleaned text and reminders")


if __name__ == "__main__":
    main()
