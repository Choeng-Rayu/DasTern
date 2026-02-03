# Test Results

This directory contains the results of OCR processing tests.

## Files
- `prescription_output.json`: Actual OCR output generated from the sample prescription using the implemented pipeline.
- `test_prescription.py`: The script used to generate this (in scripts/).

## Analysis
The result demonstrates the successful integration of:
- **Language Identification**: Detected mixed Khmer (kh) and English (en).
- **Layout Analysis**: Separated the header info from the table region (though table internal structure needs the fine-tuned model for better cell accuracy).
- **Post-processing**: Merged Khmer characters correctly in lines like "ឈ្មោះអ្នកជំងឺ: ង៉ាំ ដានី".
