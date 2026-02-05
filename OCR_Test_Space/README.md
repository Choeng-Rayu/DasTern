# OCR Test Space

This folder is for testing the OCR service.

## Structure

```
OCR_Test_Space/
├── images/          # Place test images here
├── results/         # OCR results will be saved here
└── test_ocr.py      # Test script
```

## Usage

1. Place prescription images in the `images/` folder
2. Run the test script:
   ```bash
   cd OCR_Test_Space
   python test_ocr.py
   ```
3. Results will be saved as `tesseract_result_{N}.json` in the `results/` folder

## Sample Images

Place your prescription images (JPG, PNG) in the `images/` folder.

For best results:
- Use clear, well-lit photos
- Avoid blurry images
- Include both Khmer and English text for testing
