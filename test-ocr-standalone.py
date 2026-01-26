#!/usr/bin/env python3
"""
Standalone OCR Test Script
Tests OCR functionality without Docker or database
Run with: python test-ocr-standalone.py <image_path>
"""

import sys
import json
import os
from pathlib import Path

# Add ocr-service to path
sys.path.insert(0, str(Path(__file__).parent / "ocr-service"))

from PIL import Image
import numpy as np
import cv2
from app.ocr.paddle_engine import run_ocr
from app.pipeline import process_image_simple


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def format_prescription_data(ocr_result: dict) -> dict:
    """
    Format OCR result into prescription structure
    This simulates what would be stored in the database
    """
    
    # Extract text blocks
    blocks = ocr_result.get("blocks", [])
    full_text = " ".join([block.get("text", "") for block in blocks])
    
    # Basic prescription structure
    prescription = {
        "patient_info": {
            "name": None,
            "age": None,
            "gender": None,
            "patient_id": None
        },
        "prescription_details": {
            "date": None,
            "doctor_name": None,
            "clinic_name": None,
            "diagnosis": None
        },
        "medications": [],
        "dosage_instructions": [],
        "reminder_schedule": [],
        "raw_ocr_data": {
            "full_text": full_text,
            "confidence": ocr_result.get("confidence", 0),
            "blocks_count": len(blocks),
            "language": ocr_result.get("language", "en")
        }
    }
    
    # Parse medications and dosage from blocks
    medication_keywords = ["tablet", "capsule", "mg", "ml", "dose", "syrup", "injection"]
    time_keywords = ["morning", "evening", "night", "noon", "breakfast", "lunch", "dinner", 
                     "before", "after", "times", "daily", "twice", "thrice"]
    
    current_medication = None
    
    for block in blocks:
        text = block.get("text", "").lower()
        
        # Detect medication
        if any(keyword in text for keyword in medication_keywords):
            # Try to extract medication name and dosage
            med_entry = {
                "name": block.get("text", ""),
                "dosage": "As prescribed",
                "frequency": "Unknown",
                "duration": None,
                "instructions": None
            }
            
            # Check next blocks for dosage info
            prescription["medications"].append(med_entry)
            current_medication = med_entry
        
        # Detect timing instructions
        elif any(keyword in text for keyword in time_keywords):
            instruction = {
                "text": block.get("text", ""),
                "timing": "Unknown",
                "with_food": None
            }
            prescription["dosage_instructions"].append(instruction)
            
            # If we have a current medication, link the instruction
            if current_medication:
                current_medication["instructions"] = block.get("text", "")
    
    # Generate reminder schedule based on instructions
    if prescription["dosage_instructions"]:
        for instruction in prescription["dosage_instructions"]:
            text_lower = instruction["text"].lower()
            
            # Parse timing
            times = []
            if "morning" in text_lower or "breakfast" in text_lower:
                times.append("08:00")
            if "noon" in text_lower or "lunch" in text_lower:
                times.append("12:00")
            if "evening" in text_lower or "dinner" in text_lower:
                times.append("18:00")
            if "night" in text_lower:
                times.append("21:00")
            
            # If specific times mentioned
            if "twice" in text_lower and not times:
                times = ["09:00", "21:00"]
            elif "thrice" in text_lower or "3 times" in text_lower and not times:
                times = ["08:00", "14:00", "20:00"]
            elif not times:
                times = ["09:00"]  # Default
            
            for time in times:
                prescription["reminder_schedule"].append({
                    "time": time,
                    "instruction": instruction["text"],
                    "enabled": True
                })
    
    return prescription


def main():
    """Main test function"""
    
    print_section("OCR STANDALONE TEST - NO DOCKER, NO DATABASE")
    
    # Check if image path provided
    if len(sys.argv) < 2:
        print("❌ Usage: python test-ocr-standalone.py <image_path>")
        print("\nExample:")
        print("  python test-ocr-standalone.py ./test_prescription.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Validate image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)
    
    print(f"📸 Testing OCR on: {image_path}")
    
    try:
        # Load image
        print("\n⏳ Loading image...")
        img = Image.open(image_path)
        print(f"✅ Image loaded: {img.size[0]}x{img.size[1]} pixels")
        
        # Process with OCR
        print_section("STEP 1: OCR EXTRACTION")
        print("⏳ Running PaddleOCR extraction...")
        
        # Use the simple pipeline - it takes file path
        blocks = process_image_simple(image_path)
        
        # Build ocr_result structure
        full_text = " ".join([block.get("text", "") for block in blocks])
        total_conf = sum([block.get("confidence", 0) for block in blocks])
        avg_conf = total_conf / len(blocks) if blocks else 0
        
        ocr_result = {
            "blocks": blocks,
            "confidence": avg_conf,
            "language": "en",  # You can detect this from blocks if needed
            "full_text": full_text
        }
        
        print(f"✅ OCR completed!")
        print(f"   - Language: {ocr_result.get('language', 'Unknown')}")
        print(f"   - Confidence: {ocr_result.get('confidence', 0):.2%}")
        print(f"   - Blocks detected: {len(ocr_result.get('blocks', []))}")
        
        # Display extracted text
        print_section("STEP 2: EXTRACTED TEXT BLOCKS")
        
        blocks = ocr_result.get("blocks", [])
        for i, block in enumerate(blocks, 1):
            confidence = block.get("confidence", 0)
            text = block.get("text", "")
            print(f"{i:2d}. [{confidence:5.1%}] {text}")
        
        # Format as prescription
        print_section("STEP 3: PRESCRIPTION FORMATTING")
        print("⏳ Converting OCR to prescription format...")
        
        prescription = format_prescription_data(ocr_result)
        
        # Display prescription data
        print("\n📋 PRESCRIPTION DATA:")
        print(json.dumps(prescription, indent=2, ensure_ascii=False))
        
        # Display reminder schedule
        print_section("STEP 4: REMINDER SCHEDULE")
        
        if prescription["reminder_schedule"]:
            print("⏰ Medication Reminders:\n")
            for i, reminder in enumerate(prescription["reminder_schedule"], 1):
                print(f"{i}. ⏰ {reminder['time']} - {reminder['instruction']}")
                print(f"   Status: {'✅ Enabled' if reminder['enabled'] else '❌ Disabled'}\n")
        else:
            print("⚠️  No reminder schedule could be generated.")
            print("   (No timing keywords detected in OCR text)")
        
        # Save results to file
        print_section("STEP 5: SAVING RESULTS")
        
        output_file = "test_ocr_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "ocr_result": ocr_result,
                "prescription": prescription
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_file}")
        
        # Summary
        print_section("TEST SUMMARY")
        print(f"✅ OCR Test Completed Successfully!")
        print(f"\n📊 Statistics:")
        print(f"   - Blocks extracted: {len(blocks)}")
        print(f"   - Medications found: {len(prescription['medications'])}")
        print(f"   - Dosage instructions: {len(prescription['dosage_instructions'])}")
        print(f"   - Reminders scheduled: {len(prescription['reminder_schedule'])}")
        print(f"   - Overall confidence: {ocr_result.get('confidence', 0):.2%}")
        
        if ocr_result.get('confidence', 0) < 0.7:
            print(f"\n⚠️  Warning: Low confidence OCR result")
            print(f"   Consider using a clearer image or adjusting lighting")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error during OCR processing:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
