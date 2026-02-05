"""
Prescription OCR Test Script
Tests OCR service and AI enhancement pipeline
Stores both raw OCR results and AI-enhanced results
"""

import asyncio
import json
import time
import requests
import nest_asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Allow nested event loops (useful for running in some environments)
nest_asyncio.apply()

# Configuration - read from environment with default
AI_LLM_SERVICE_URL = os.getenv("AI_LLM_SERVICE_URL", "http://localhost:8001")
OCR_LANGUAGES = "eng+khm+fra"

# Test images directory
TEST_IMAGES_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/images")
RESULTS_DIR = Path("/home/rayu/DasTern/ocr-service-anti/tests/results")


def call_ai_enhancement(raw_ocr_data: Dict[str, Any], base_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Call AI-LLM service to enhance OCR data with structured output
    
    Args:
        raw_ocr_data: Raw OCR output from OCR service
        base_date: Starting date for reminders (YYYY-MM-DD format)
    
    Returns:
        AI-enhanced prescription data with reminders
    """
    if base_date is None:
        base_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.post(
            f"{AI_LLM_SERVICE_URL}/api/v1/prescription/enhance-and-generate-reminders",
            json={
                "ocr_data": raw_ocr_data,
                "base_date": base_date
            },
            timeout=180  # 3 minutes for AI processing
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"AI service error: {response.status_code} - {response.text}"
            }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "AI service timeout (180s)"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to AI service. Is it running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def process_single_image(image_path: Path, pipeline) -> Dict[str, Any]:
    """
    Process a single image through OCR pipeline
    
    Args:
        image_path: Path to the image file
        pipeline: Initialized OCR pipeline
    
    Returns:
        OCR result as dictionary
    """
    print(f"\n{'='*60}")
    print(f"Processing: {image_path.name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Read image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Run OCR pipeline
        result = await pipeline.process(
            image_bytes=image_bytes,
            filename=image_path.name,
            languages=OCR_LANGUAGES
        )
        
        ocr_time = time.time() - start_time
        result_json = result.model_dump(mode='json')
        
        print(f"OCR completed in {ocr_time:.2f}s")
        print(f"  - Quality: Blur={result.quality.blur}, Contrast={result.quality.contrast}")
        print(f"  - Blocks detected: {len(result.blocks)}")
        print(f"  - Text length: {len(result.raw_text)} chars")
        
        return {
            "success": True,
            "data": result_json,
            "processing_time_ms": ocr_time * 1000
        }
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_test_images() -> List[Path]:
    """Get list of test images to process"""
    images = []
    
    # Check configured test images directory
    if TEST_IMAGES_DIR.exists():
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            images.extend(TEST_IMAGES_DIR.glob(ext))
    
    # Also check local tests directory
    local_tests = Path("tests")
    if local_tests.exists():
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            images.extend(local_tests.glob(ext))
    
    return sorted(images)


async def run_test():
    """Main test function - processes images one by one"""
    from app.core.pipeline import OCRPipeline
    
    # Setup directories
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw_dir = RESULTS_DIR / "raw"
    enhanced_dir = RESULTS_DIR / "enhanced"
    raw_dir.mkdir(exist_ok=True)
    enhanced_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("PRESCRIPTION OCR & AI ENHANCEMENT TEST")
    print("=" * 70)
    print(f"Results directory: {RESULTS_DIR}")
    print(f"AI Service: {AI_LLM_SERVICE_URL}")
    
    # Get test images
    images = get_test_images()
    
    if not images:
        print("\nNo test images found!")
        print(f"Please add images to: {TEST_IMAGES_DIR}")
        return
    
    print(f"\nFound {len(images)} test image(s):")
    for img in images:
        print(f"  - {img.name}")
    
    # Initialize OCR pipeline
    print("\nInitializing OCR pipeline...")
    pipeline = OCRPipeline()
    
    # Check AI service availability
    print("\nChecking AI service availability...")
    try:
        response = requests.get(f"{AI_LLM_SERVICE_URL}/health", timeout=5)
        ai_available = response.status_code == 200
        print(f"AI Service: {'Available' if ai_available else 'Not available'}")
    except:
        ai_available = False
        print("AI Service: Not available (will skip enhancement)")
    
    # Process each image
    results_summary = []
    base_date = datetime.now().strftime("%Y-%m-%d")
    
    for idx, image_path in enumerate(images, 1):
        print(f"\n[{idx}/{len(images)}] Processing {image_path.name}...")
        
        # Step 1: Run OCR
        ocr_result = await process_single_image(image_path, pipeline)
        
        # Save raw OCR result
        raw_filename = f"{image_path.stem}_raw.json"
        raw_filepath = raw_dir / raw_filename
        with open(raw_filepath, "w", encoding='utf-8') as f:
            json.dump(ocr_result, f, indent=2, ensure_ascii=False)
        print(f"  Raw OCR saved: {raw_filename}")
        
        # Step 2: AI Enhancement (if available)
        enhanced_result = None
        if ai_available and ocr_result.get("success"):
            print("  Sending to AI service for enhancement...")
            start_time = time.time()
            
            enhanced_result = call_ai_enhancement(
                ocr_result["data"],
                base_date=base_date
            )
            
            ai_time = time.time() - start_time
            
            if enhanced_result.get("success"):
                print(f"  AI enhancement completed in {ai_time:.2f}s")
                if "metadata" in enhanced_result:
                    total_meds = enhanced_result.get("metadata", {}).get("total_medications", 0)
                    total_reminders = enhanced_result.get("metadata", {}).get("total_reminders", 0)
                    print(f"  - Medications found: {total_meds}")
                    print(f"  - Reminders generated: {total_reminders}")
            else:
                print(f"  AI enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
            
            # Save enhanced result
            enhanced_filename = f"{image_path.stem}_enhanced.json"
            enhanced_filepath = enhanced_dir / enhanced_filename
            with open(enhanced_filepath, "w", encoding='utf-8') as f:
                json.dump(enhanced_result, f, indent=2, ensure_ascii=False)
            print(f"  Enhanced result saved: {enhanced_filename}")
        
        # Track summary
        results_summary.append({
            "image": image_path.name,
            "ocr_success": ocr_result.get("success", False),
            "ocr_time_ms": ocr_result.get("processing_time_ms", 0),
            "ai_success": enhanced_result.get("success", False) if enhanced_result else False,
            "medications_found": enhanced_result.get("metadata", {}).get("total_medications", 0) if enhanced_result else 0,
            "reminders_generated": enhanced_result.get("metadata", {}).get("total_reminders", 0) if enhanced_result else 0
        })
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for result in results_summary:
        status = "OK" if result["ocr_success"] else "FAILED"
        ai_status = "OK" if result["ai_success"] else "FAILED"
        print(f"\n{result['image']}:")
        print(f"  OCR: {status} ({result['ocr_time_ms']:.0f}ms)")
        print(f"  AI: {ai_status}")
        print(f"  Medications: {result['medications_found']}, Reminders: {result['reminders_generated']}")
    
    # Save summary
    summary_file = RESULTS_DIR / "test_summary.json"
    with open(summary_file, "w", encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_images": len(images),
            "ai_service_available": ai_available,
            "results": results_summary
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSummary saved to: {summary_file}")
    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(run_test())
