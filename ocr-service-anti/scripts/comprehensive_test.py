"""
Comprehensive Prescription OCR & AI Enhancement Test Script
============================================================

This script tests the complete pipeline:
1. OCR service processes prescription images
2. Stores raw OCR output in timestamped folders
3. Sends to AI-LLM service for enhancement
4. Validates output matches required JSON format
5. Stores final enhanced results

Output Format Target:
{
  "patient_info": {...},
  "medications": [...],
  "daily_reminders": [...],
  "summary": {...}
}
"""

import asyncio
import json
import time
import requests
import nest_asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import sys

# Allow nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/home/rayu/DasTern/ocr-service-anti/tests/results/test.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
OCR_SERVICE_URL = "http://localhost:8000"
AI_LLM_SERVICE_URL = "http://localhost:8001"
OCR_LANGUAGES = "eng+khm+fra"

# Directories
TEST_IMAGES_DIR = Path("/home/rayu/DasTern/OCR_Test_Space/images")
RESULTS_BASE_DIR = Path("/home/rayu/DasTern/ocr-service-anti/tests/results")
RAW_RESULTS_DIR = RESULTS_BASE_DIR / "raw"
FINAL_RESULTS_DIR = RESULTS_BASE_DIR / "final"

# Target JSON format for validation
TARGET_FORMAT = {
    "patient_info": {
        "required_fields": ["patient_id", "patient_name", "diagnosis", "prescription_date"],
        "optional_fields": []
    },
    "medications": {
        "required_fields": ["medication_id", "name", "dosage", "duration_days", "start_date", "end_date", "route", "route_description", "notes", "schedule"],
        "schedule_fields": ["time_slot", "time", "time_range", "quantity", "unit"]
    },
    "daily_reminders": {
        "required_fields": ["day_number", "date", "day_of_week", "reminders"],
        "reminder_fields": ["time", "time_slot", "time_range", "medications_to_take"]
    },
    "summary": {
        "required_fields": ["total_medications", "max_duration_days", "reminder_times", "routes_used"]
    }
}


class TestSession:
    """Manages a single test session with timestamped folders"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.raw_dir = RAW_RESULTS_DIR / self.timestamp
        self.final_dir = FINAL_RESULTS_DIR / self.timestamp
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.final_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def log_result(self, image_name: str, ocr_success: bool, ai_success: bool, 
                   ocr_time: float, ai_time: float, validation_result: Dict):
        """Log result for an image"""
        self.results.append({
            "image": image_name,
            "ocr_success": ocr_success,
            "ai_success": ai_success,
            "ocr_time_ms": round(ocr_time * 1000, 2),
            "ai_time_ms": round(ai_time * 1000, 2) if ai_time else None,
            "format_valid": validation_result.get("valid", False),
            "validation_errors": validation_result.get("errors", []),
            "timestamp": datetime.now().isoformat()
        })
        
    def save_summary(self):
        """Save test session summary"""
        summary = {
            "session_id": self.timestamp,
            "test_date": datetime.now().isoformat(),
            "total_images": len(self.results),
            "ocr_success_count": sum(1 for r in self.results if r["ocr_success"]),
            "ai_success_count": sum(1 for r in self.results if r["ai_success"]),
            "format_valid_count": sum(1 for r in self.results if r["format_valid"]),
            "average_ocr_time_ms": sum(r["ocr_time_ms"] for r in self.results) / len(self.results) if self.results else 0,
            "results": self.results
        }
        
        summary_path = RESULTS_BASE_DIR / f"summary_{self.timestamp}.json"
        with open(summary_path, "w", encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary


def validate_output_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate if the output matches the target JSON format
    
    Returns:
        Dict with 'valid' boolean and list of 'errors'
    """
    errors = []
    warnings = []
    
    # Check patient_info
    if "patient_info" not in data:
        errors.append("Missing 'patient_info' section")
    else:
        patient = data["patient_info"]
        for field in TARGET_FORMAT["patient_info"]["required_fields"]:
            if field not in patient:
                errors.append(f"patient_info missing required field: {field}")
    
    # Check medications
    if "medications" not in data:
        errors.append("Missing 'medications' section")
    elif not isinstance(data["medications"], list):
        errors.append("'medications' should be a list")
    else:
        for i, med in enumerate(data["medications"]):
            for field in ["medication_id", "name", "dosage", "schedule"]:
                if field not in med:
                    errors.append(f"medications[{i}] missing field: {field}")
            
            if "schedule" in med and isinstance(med["schedule"], list):
                for j, sched in enumerate(med["schedule"]):
                    for field in ["time_slot", "time", "quantity"]:
                        if field not in sched:
                            warnings.append(f"medications[{i}].schedule[{j}] missing: {field}")
    
    # Check daily_reminders
    if "daily_reminders" not in data:
        errors.append("Missing 'daily_reminders' section")
    elif not isinstance(data["daily_reminders"], list):
        errors.append("'daily_reminders' should be a list")
    else:
        for i, day in enumerate(data["daily_reminders"]):
            for field in ["day_number", "date", "day_of_week", "reminders"]:
                if field not in day:
                    errors.append(f"daily_reminders[{i}] missing field: {field}")
    
    # Check summary
    if "summary" not in data:
        errors.append("Missing 'summary' section")
    else:
        summary = data["summary"]
        for field in TARGET_FORMAT["summary"]["required_fields"]:
            if field not in summary:
                errors.append(f"summary missing required field: {field}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


async def process_single_image_ocr(image_path: Path) -> Dict[str, Any]:
    """
    Process a single image through OCR pipeline directly (not via API)
    
    Returns:
        OCR result dictionary with timing information
    """
    # Import here to avoid issues when running outside the environment
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from app.core.pipeline import OCRPipeline
    
    logger.info(f"Processing image: {image_path.name}")
    
    start_time = time.time()
    
    try:
        # Read image bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Initialize pipeline
        pipeline = OCRPipeline()
        
        # Process image
        result = await pipeline.process(
            image_bytes=image_bytes,
            filename=image_path.name,
            languages=OCR_LANGUAGES
        )
        
        processing_time = time.time() - start_time
        
        # Convert result to dict
        result_dict = result.model_dump(mode='json')
        
        logger.info(f"  ✓ OCR completed in {processing_time:.2f}s")
        logger.info(f"    - Quality: blur={result.quality.blur.value}({result.quality.blur_score:.1f}), contrast={result.quality.contrast.value}({result.quality.contrast_score:.1f})")
        logger.info(f"    - Blocks detected: {len(result.blocks)}")
        logger.info(f"    - Raw text length: {len(result.raw_text)} chars")
        
        return {
            "success": True,
            "data": result_dict,
            "processing_time_seconds": processing_time,
            "image_name": image_path.name
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"  ✗ OCR failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "processing_time_seconds": processing_time,
            "image_name": image_path.name
        }


def call_ai_enhancement(ocr_data: Dict[str, Any], base_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Call AI-LLM service to enhance OCR data
    
    Args:
        ocr_data: Raw OCR output
        base_date: Starting date for reminders (YYYY-MM-DD)
        
    Returns:
        AI-enhanced prescription data
    """
    if base_date is None:
        base_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info("  Sending to AI service for enhancement...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{AI_LLM_SERVICE_URL}/api/v1/prescription/enhance-and-generate-reminders",
            json={
                "ocr_data": ocr_data,
                "base_date": base_date
            },
            timeout=180  # 3 minutes for AI processing
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"  ✓ AI enhancement completed in {processing_time:.2f}s")
            result["processing_time_seconds"] = processing_time
            return result
        else:
            logger.error(f"  ✗ AI service error: {response.status_code}")
            return {
                "success": False,
                "error": f"AI service error: {response.status_code} - {response.text}",
                "processing_time_seconds": processing_time
            }
            
    except requests.exceptions.Timeout:
        processing_time = time.time() - start_time
        logger.error("  ✗ AI service timeout (180s)")
        return {
            "success": False,
            "error": "AI service timeout (180s)",
            "processing_time_seconds": processing_time
        }
    except requests.exceptions.ConnectionError:
        logger.error("  ✗ Cannot connect to AI service")
        return {
            "success": False,
            "error": "Cannot connect to AI service. Is it running on port 8001?"
        }
    except Exception as e:
        logger.error(f"  ✗ AI service error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def check_services() -> Dict[str, bool]:
    """Check if required services are running"""
    status = {"ocr": False, "ai": False}
    
    # Check AI service (OCR uses direct pipeline, not API)
    try:
        response = requests.get(f"{AI_LLM_SERVICE_URL}/health", timeout=5)
        status["ai"] = response.status_code == 200
    except:
        pass
    
    # OCR uses direct pipeline import
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from app.core.pipeline import OCRPipeline
        status["ocr"] = True
    except Exception as e:
        logger.error(f"OCR pipeline import failed: {e}")
    
    return status


def get_test_images() -> List[Path]:
    """Get list of test images"""
    images = []
    
    if TEST_IMAGES_DIR.exists():
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            images.extend(TEST_IMAGES_DIR.glob(ext))
    
    return sorted(images)


async def run_comprehensive_test():
    """Main test function"""
    print("=" * 70)
    print("PRESCRIPTION OCR & AI ENHANCEMENT - COMPREHENSIVE TEST")
    print("=" * 70)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Create test session
    session = TestSession()
    logger.info(f"Test session ID: {session.timestamp}")
    logger.info(f"Raw results: {session.raw_dir}")
    logger.info(f"Final results: {session.final_dir}")
    print()
    
    # Check services
    print("Checking services...")
    services = check_services()
    print(f"  OCR Pipeline: {'✓ Ready' if services['ocr'] else '✗ Not available'}")
    print(f"  AI Service:   {'✓ Running' if services['ai'] else '✗ Not running'}")
    
    if not services["ocr"]:
        print("\nERROR: OCR pipeline not available. Check your environment.")
        return
    
    # Get test images
    images = get_test_images()
    
    if not images:
        print(f"\nNo test images found in: {TEST_IMAGES_DIR}")
        print("Please add prescription images (.png, .jpg, .jpeg)")
        return
    
    print(f"\nFound {len(images)} test image(s):")
    for img in images:
        print(f"  - {img.name}")
    print()
    
    # Process each image one by one
    base_date = datetime.now().strftime("%Y-%m-%d")
    
    for idx, image_path in enumerate(images, 1):
        print(f"\n{'='*60}")
        print(f"[{idx}/{len(images)}] {image_path.name}")
        print(f"{'='*60}")
        
        # Step 1: OCR Processing
        print("\n1. Running OCR...")
        ocr_result = await process_single_image_ocr(image_path)
        
        # Save raw OCR result
        raw_filename = f"{image_path.stem}_raw.json"
        raw_filepath = session.raw_dir / raw_filename
        with open(raw_filepath, "w", encoding='utf-8') as f:
            json.dump(ocr_result, f, indent=2, ensure_ascii=False)
        print(f"   Raw result saved: {raw_filename}")
        
        # Also save raw text separately for easier viewing
        if ocr_result.get("success") and ocr_result.get("data", {}).get("raw_text"):
            raw_text_filename = f"{image_path.stem}_raw.txt"
            raw_text_filepath = session.raw_dir / raw_text_filename
            with open(raw_text_filepath, "w", encoding='utf-8') as f:
                f.write(ocr_result["data"]["raw_text"])
            print(f"   Raw text saved: {raw_text_filename}")
        
        # Step 2: AI Enhancement (if OCR succeeded and AI is available)
        ai_result = None
        ai_time = 0
        validation_result = {"valid": False, "errors": ["OCR failed or AI not available"]}
        
        if ocr_result.get("success") and services["ai"]:
            print("\n2. Running AI Enhancement...")
            ai_result = call_ai_enhancement(ocr_result["data"], base_date)
            ai_time = ai_result.get("processing_time_seconds", 0)
            
            if ai_result.get("success"):
                # Step 3: Validate output format
                print("\n3. Validating output format...")
                validation_result = validate_output_format(ai_result)
                
                if validation_result["valid"]:
                    print("   ✓ Output format is valid!")
                else:
                    print(f"   ✗ Format validation failed with {len(validation_result['errors'])} error(s):")
                    for error in validation_result["errors"][:5]:  # Show first 5 errors
                        print(f"     - {error}")
                
                # Save final result
                final_filename = f"{image_path.stem}_final.json"
                final_filepath = session.final_dir / final_filename
                with open(final_filepath, "w", encoding='utf-8') as f:
                    json.dump(ai_result, f, indent=2, ensure_ascii=False)
                print(f"\n   Final result saved: {final_filename}")
            else:
                print(f"   AI enhancement failed: {ai_result.get('error', 'Unknown error')}")
                validation_result = {"valid": False, "errors": [ai_result.get('error', 'Unknown')]}
        elif not services["ai"]:
            print("\n2. Skipping AI Enhancement (service not available)")
        
        # Log result
        session.log_result(
            image_name=image_path.name,
            ocr_success=ocr_result.get("success", False),
            ai_success=ai_result.get("success", False) if ai_result else False,
            ocr_time=ocr_result.get("processing_time_seconds", 0),
            ai_time=ai_time,
            validation_result=validation_result
        )
    
    # Print and save summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    summary = session.save_summary()
    
    print(f"\nSession ID: {summary['session_id']}")
    print(f"Total images tested: {summary['total_images']}")
    print(f"OCR success: {summary['ocr_success_count']}/{summary['total_images']}")
    print(f"AI success: {summary['ai_success_count']}/{summary['total_images']}")
    print(f"Format valid: {summary['format_valid_count']}/{summary['total_images']}")
    print(f"Average OCR time: {summary['average_ocr_time_ms']:.0f}ms")
    
    print(f"\nResults saved to:")
    print(f"  Raw: {session.raw_dir}")
    print(f"  Final: {session.final_dir}")
    print(f"  Summary: {RESULTS_BASE_DIR / f'summary_{session.timestamp}.json'}")
    
    # Return summary for programmatic use
    return summary


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
