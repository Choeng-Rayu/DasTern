#!/usr/bin/env python3
"""
Enhanced Medical OCR Test Script
Tests the improved OCR service with medical prescription images
Saves results with numbered outputs in OCR_Test_Space/results
"""
import sys
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

# Add ocr-service to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ocr-service"))

from app.ocr.extractors.medical_ocr import extract_medical_prescription
from app.core.logger import logger


# Configuration
IMAGES_DIR = Path(__file__).parent / "images"
RESULTS_DIR = Path(__file__).parent / "results"

# Ensure results directory exists
RESULTS_DIR.mkdir(exist_ok=True)


def get_next_result_number() -> int:
    """Get the next available result number"""
    existing = list(RESULTS_DIR.glob("result_*.json"))
    if not existing:
        return 1
    
    numbers = []
    for f in existing:
        try:
            num = int(f.stem.split('_')[1])
            numbers.append(num)
        except (IndexError, ValueError):
            continue
    
    return max(numbers) + 1 if numbers else 1


def load_image(image_path: Path) -> np.ndarray:
    """Load image from file"""
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    return image


def save_results(result_num: int, image_name: str, ocr_results: dict, processing_time: float):
    """Save results to JSON file"""
    output_data = {
        "result_number": result_num,
        "timestamp": datetime.now().isoformat(),
        "image_name": image_name,
        "processing_time_seconds": processing_time,
        "ocr_results": ocr_results
    }
    
    output_path = RESULTS_DIR / f"result_{result_num}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return output_path


def print_summary(result_num: int, image_name: str, ocr_results: dict, processing_time: float):
    """Print a summary of the OCR results"""
    print("\n" + "=" * 80)
    print(f"RESULT #{result_num}: {image_name}")
    print("=" * 80)
    print(f"Processing Time: {processing_time:.2f} seconds")
    
    # Stats
    stats = ocr_results.get('stats', {})
    print(f"\nOCR Stats:")
    print(f"  Total words: {stats.get('total_words', 0)}")
    print(f"  Average confidence: {stats.get('avg_confidence', 0):.1f}%")
    print(f"  Min confidence: {stats.get('min_confidence', 0):.1f}%")
    print(f"  Max confidence: {stats.get('max_confidence', 0):.1f}%")
    
    # Table detection
    table_info = ocr_results.get('table_detection', {})
    if table_info.get('found'):
        table_data = table_info.get('data', {})
        print(f"\nTable Detected:")
        print(f"  Rows: {table_data.get('rows', 0)}")
        print(f"  Columns: {table_data.get('columns', 0)}")
        print(f"  Cells: {len(table_data.get('cells', []))}")
    
    # Structured data
    structured = ocr_results.get('structured_data', {})
    if structured:
        print(f"\nStructured Data Extracted:")
        
        # Patient info
        patient = structured.get('patient', {})
        if any(patient.values()):
            print(f"  Patient:")
            if patient.get('name'):
                print(f"    Name: {patient['name']}")
            if patient.get('id'):
                print(f"    ID: {patient['id']}")
            if patient.get('age'):
                print(f"    Age: {patient['age']}")
            if patient.get('gender'):
                print(f"    Gender: {patient['gender']}")
        
        # Doctor info
        doctor = structured.get('doctor', {})
        if doctor.get('name'):
            print(f"  Doctor: {doctor['name']}")
        
        # Medications
        medications = structured.get('medications', [])
        if medications:
            print(f"  Medications ({len(medications)}):")
            for idx, med in enumerate(medications, 1):
                print(f"    {idx}. {med['name']}")
                if med.get('dosage'):
                    print(f"       Dosage: {med['dosage']}")
                if med.get('frequency'):
                    print(f"       Frequency: {med['frequency']}")
        
        # Table medications
        table_meds = structured.get('table_medications', [])
        if table_meds:
            print(f"  Medications from Table ({len(table_meds)}):")
            for idx, med in enumerate(table_meds, 1):
                print(f"    {idx}. {med['name']}")
                if med.get('dosage'):
                    print(f"       Dosage: {med['dosage']}")
                if med.get('frequency'):
                    print(f"       Frequency: {med['frequency']}")
        
        # Dates
        dates = structured.get('dates', [])
        if dates:
            print(f"  Dates ({len(dates)}):")
            for date in dates:
                print(f"    {date['date_string']}", end='')
                if date.get('parsed_date'):
                    print(f" (parsed: {date['parsed_date']})", end='')
                print()
        
        # Time of day
        time_of_day = structured.get('time_of_day', [])
        if time_of_day:
            print(f"  Time of Day: {', '.join(time_of_day)}")
    
    print("=" * 80)


def process_image(image_path: Path, result_num: int):
    """Process a single image"""
    print(f"\n{'*' * 80}")
    print(f"Processing: {image_path.name}")
    print(f"{'*' * 80}")
    
    try:
        # Load image
        print("Loading image...")
        image = load_image(image_path)
        print(f"Image size: {image.shape[1]}x{image.shape[0]}")
        
        # Run OCR
        print("Running enhanced medical OCR...")
        import time
        start_time = time.time()
        
        ocr_results = extract_medical_prescription(
            image,
            apply_advanced_preprocessing=True,
            detect_tables=True,
            extract_structured=True,
            languages="khm+eng+fra",
            upscale_factor=1.5
        )
        
        processing_time = time.time() - start_time
        
        # Save results
        output_path = save_results(result_num, image_path.name, ocr_results, processing_time)
        print(f"\nResults saved to: {output_path}")
        
        # Print summary
        print_summary(result_num, image_path.name, ocr_results, processing_time)
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error processing {image_path.name}: {e}")
        logger.error(f"Error processing {image_path.name}", exc_info=True)
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("ENHANCED MEDICAL OCR TEST")
    print("=" * 80)
    print(f"Images directory: {IMAGES_DIR}")
    print(f"Results directory: {RESULTS_DIR}")
    
    # Find all images
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.tif', '*.tiff']
    image_files = []
    for ext in image_extensions:
        image_files.extend(IMAGES_DIR.glob(ext))
    
    # Remove .gitkeep if present
    image_files = [f for f in image_files if f.name != '.gitkeep']
    
    # Sort by name
    image_files.sort()
    
    if not image_files:
        print("\n❌ No images found in images directory!")
        return
    
    print(f"\nFound {len(image_files)} image(s) to process:")
    for img in image_files:
        print(f"  - {img.name}")
    
    # Get starting result number
    start_num = get_next_result_number()
    print(f"\nStarting from result number: {start_num}")
    
    # Process each image
    successful = 0
    failed = 0
    
    for idx, image_path in enumerate(image_files):
        result_num = start_num + idx
        
        if process_image(image_path, result_num):
            successful += 1
        else:
            failed += 1
    
    # Final summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total images: {len(image_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nResults saved to: {RESULTS_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
