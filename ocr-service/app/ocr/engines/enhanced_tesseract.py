"""
Enhanced Tesseract OCR Engine for Cambodian Prescriptions
Optimized preprocessing for better mixed-language accuracy
"""
import os
import pytesseract
import cv2
import numpy as np
from pytesseract import Output
from typing import Dict, List, Any, Optional
from ...core.config import settings
from ...core.logger import logger

def fix_medical_terms(text: str) -> str:
    """Fix common medical term OCR errors in mixed languages"""
    medical_corrections = {
        # English medical terms
        'Paracetamol': 'Paracetamol',
        'Amoxicillin': 'Amoxicillin', 
        'Ibuprofen': 'Ibuprofen',
        'Metformin': 'Metformin',
        'Insulin': 'Insulin',
        'Glibenclamide': 'Glibenclamide',
        
        # Common dosage corrections
        'mg': 'mg',
        'g': 'g',
        'tablet': 'tablet',
        'capsule': 'capsule',
        
        # Khmer medical terms (common OCR errors)
        'ថ្ងៃ': 'ថ្ងៃ',  # day
        'ព្រឹក': 'ព្រឹក',  # morning
        'ល្ងាច': 'ល្ងាច',  # evening
        'យប់': 'យប់',  # night
        'និង': 'និង',  # and
        'សម្រាប់': 'សម្រាប់',  # for
        
        # French medical terms
        'matin': 'matin',
        'soir': 'soir', 
        'nuit': 'nuit',
        'comprimé': 'comprimé',
        'gélule': 'gélule',
    }
    
    corrected = text
    for wrong, right in medical_corrections.items():
        if text.lower() == wrong.lower():
            corrected = right
            break
    
    return corrected

def fix_common_ocr_errors(text: str) -> str:
    """Fix common OCR errors for prescription text"""
    # Number corrections (0-9)
    number_corrections = {
        'O': '0', 'o': '0',
        'I': '1', 'l': '1', '|': '1',
        'Z': '2', 'z': '2',
        'S': '5', 's': '5',
        'G': '6', 'g': '6',
        'T': '7', 't': '7',
        'B': '8', 'g': '8'
    }
    
    # Apply number corrections for dosage information
    corrected = text
    for wrong, right in number_corrections.items():
        # Only replace if context suggests it's a number
        if any(char.isdigit() for char in text) or wrong in text:
            corrected = corrected.replace(wrong, right)
    
    # Fix common punctuation errors
    corrected = corrected.replace(',', '.')
    corrected = corrected.replace(';', ',')
    
    return corrected

def is_medical_term(text: str) -> bool:
    """Check if text contains medical terms"""
    medical_keywords = [
        'paracetamol', 'amoxicillin', 'ibuprofen', 'metformin', 'insulin',
        'glibenclamide', 'mg', 'tablet', 'capsule', 'dose', ' dosage',
        'ថ្ងៃ', 'ព្រឹក', 'ល្ងាច', 'យប់',  # Khmer time/medical
        'matin', 'soir', 'nuit', 'comprimé', 'gélule'  # French medical
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in medical_keywords)

def detect_dominant_language(text_list: List[str]) -> str:
    """Detect dominant language from OCR text"""
    khmer_chars = set('កខគឃងចឆជឈញដឋឌឍណតថទធនបផពមយរលវសហឡអឣឤឥឦឧឪឮឰឲឳ឴឵ិីឹឺុូួើឿ')
    french_chars = set('àâäéèêëïîôöùûüÿç')
    english_chars = set('abcdefghijklmnopqrstuvwxyz')
    
    khmer_count = 0
    french_count = 0 
    english_count = 0
    
    for text in text_list:
        for char in text.lower():
            if char in khmer_chars:
                khmer_count += 1
            elif char in french_chars:
                french_count += 1
            elif char in english_chars:
                english_count += 1
    
    total = khmer_count + french_count + english_count
    if total == 0:
        return 'unknown'
    
    # Determine dominant language
    if khmer_count / total > 0.3:
        return 'khmer+mixed'
    elif french_count / total > 0.2:
        return 'french+mixed' 
    elif english_count / total > 0.5:
        return 'english+mixed'
    else:
        return 'mixed'

def fix_khmer_ocr_errors(text: str) -> str:
    """
    Fix common Khmer OCR recognition errors
    
    Args:
        text: Raw OCR text
        
    Returns:
        Corrected text
    """
    # Common Khmer OCR corrections
    corrections = {
        'ក': 'ក',  # Common character confusions
        'ខ': 'ខ',
        'គ': 'គ', 
        'ឃ': 'ឃ',
        'ង': 'ង',
        'ច': 'ច',
        'ឆ': 'ឆ',
        'ជ': 'ជ',
        'ៈ': 'ឈ',
        'ញ': 'ញ',
        'ដ': 'ដ',
        'ឋ': 'ឋ',
        'ឌ': 'ឌ',
        'ឍ': 'ឍ',
        'ណ': 'ណ',
        'ត': 'ត',
        'ថ': 'ថ',
        'ទ': 'ទ',
        'ធ': 'ធ',
        'ន': 'ន',
        'ប': 'ប',
        'ផ': 'ផ',
        'ព': 'ព',
        'ភ': 'ភ',
        'ម': 'ម',
        'យ': 'យ',
        'រ': 'រ',
        'ល': 'ល',
        'វ': 'វ',
        'ស': 'ស',
        'ហ': 'ហ',
        'ឡ': 'ឡ',
        'អ': 'អ',
        'ឣ': 'ឣ',
        'ឤ': 'ឤ',
        'ឥ': 'ឥ',
        'ឦ': 'ឦ',
        'ឧ': 'ឧ',
        'ឪ': 'ឪ',
        'ឮ': 'ឮ',
        'ឯ': 'ឯ',
        'ឰ': 'ឰ',
        'ឲ': 'ឲ',
        'ឳ': 'ឳ',
        '឴': '឴',
        '឵': '឵',
        'ិ': 'ិ',
        'ី': 'ី',
        'ឹ': 'ឹ',
        'ឺ': 'ឺ',
        'ុ': 'ុ',
        'ូ': 'ូ',
        'ួ': 'ួ',
        'ើ': 'ើ',
        'ឿ': 'ឿ',
    }
    
    # Apply corrections
    corrected = text
    for wrong, right in corrections.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

def preprocess_prescription_image(image: np.ndarray) -> np.ndarray:
    """
    Enhanced preprocessing for prescription images
    
    Args:
        image: Input image array
        
    Returns:
        Preprocessed image array optimized for OCR
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply adaptive thresholding for better text contrast
        # This helps with mixed languages and handwritten text
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise slightly to clean up
        denoised = cv2.medianBlur(binary, 3)
        
        # Enhance contrast for better OCR
        enhanced = cv2.convertScaleAbs(denoised, alpha=1.2, beta=10)
        
        logger.info("Applied enhanced preprocessing for prescription OCR")
        return enhanced
        
    except Exception as e:
        logger.warning(f"Preprocessing failed, using original: {str(e)}")
        return image

def post_process_ocr_results(data: Dict[str, List]) -> Dict[str, List]:
    """
    Post-process OCR results to improve quality for mixed-language prescriptions
    
    Args:
        data: Raw OCR data from Tesseract
        
    Returns:
        Improved OCR data in standard Tesseract format
    """
    try:
        # Initialize improved data structure with all required keys
        improved_data = {
            'text': [],
            'conf': [],
            'left': [],
            'top': [],
            'width': [],
            'height': [],
            'block_num': [],
            'par_num': [],
            'line_num': [],
            'word_num': []
        }
        
        # Process each OCR element
        for i in range(len(data.get('text', []))):
            text = data.get('text', [])[i]
            conf = data.get('conf', [])[i]
            
            # Skip empty or very low confidence text
            if not text or not text.strip() or conf < 20:
                continue
                
            # Apply text improvements
            text = text.strip()
            text = fix_khmer_ocr_errors(text)
            text = fix_medical_terms(text)
            
            # Boost confidence for known medical terms
            if is_medical_term(text):
                conf = min(conf + 15, 100)  # Boost confidence but cap at 100
            
            # Keep only improved results
            if conf >= 30 and text:
                improved_data['text'].append(text)
                improved_data['conf'].append(conf)
                improved_data['left'].append(data.get('left', [])[i] if 'left' in data else 0)
                improved_data['top'].append(data.get('top', [])[i] if 'top' in data else 0)
                improved_data['width'].append(data.get('width', [])[i] if 'width' in data else 0)
                improved_data['height'].append(data.get('height', [])[i] if 'height' in data else 0)
                improved_data['block_num'].append(data.get('block_num', [])[i] if 'block_num' in data else 0)
                improved_data['par_num'].append(data.get('par_num', [])[i] if 'par_num' in data else 0)
                improved_data['line_num'].append(data.get('line_num', [])[i] if 'line_num' in data else 0)
                improved_data['word_num'].append(data.get('word_num', [])[i] if 'word_num' in data else 0)
        
        avg_conf = sum(improved_data['conf']) / len(improved_data['conf']) if improved_data['conf'] else 0
        logger.info(f"Post-processed OCR: {len(improved_data['text'])} elements, avg confidence: {avg_conf:.1f}%")
        
        return improved_data
        
    except Exception as e:
        logger.warning(f"Post-processing failed, using original: {str(e)}")
        return data

def run_enhanced_ocr(
    image: np.ndarray,
    languages: Optional[str] = None,
    oem: Optional[int] = None,
    psm: Optional[int] = None,
    user_words_path: Optional[str] = None
) -> Dict[str, List]:
    """
    Enhanced OCR with optimized configuration for Cambodian prescriptions
    
    Args:
        image: Input image (numpy array)
        languages: Language string (e.g., "khm+eng+fra")
        oem: OCR Engine Mode (0-3)
        psm: Page Segmentation Mode (0-13)
        user_words_path: Path to user words file
        
    Returns:
        Dictionary containing OCR data with text, confidence, and positions
    """
    # Use settings defaults if not provided
    lang = languages or settings.OCR_LANGUAGES
    engine_mode = oem if oem is not None else settings.OCR_OEM
    page_seg_mode = psm if psm is not None else settings.OCR_PSM
    user_words = user_words_path or settings.USER_WORDS_PATH
    
    # Enhanced preprocessing
    processed_image = preprocess_prescription_image(image)
    
    # Build optimized config for mixed-language prescriptions
    config_parts = [
        f"--oem {engine_mode}",
        f"--psm {page_seg_mode}",
        # Use single character mode for better Khmer recognition
        "--tessdata-dir /usr/share/tesseract/tessdata",
        # Optimize for medical text
        "--dpi 300",
        # Enable character whitelist for common prescription characters
        "-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzកខគឃងចឆជឈញដឋឌឍណតថទធនបផពមយរលវសហឡអឣឤឥឦឧឪឮឰឲឳ឴឵ិីឹឺុូួើឿ.,-+|/:()[]",
    ]
    
    # Add user words if available and file exists
    if user_words and os.path.exists(user_words):
        config_parts.append(f"--user-words {user_words}")
    
    config = " ".join(config_parts)
    
    logger.info(f"Running enhanced OCR with lang={lang}, config={config}")
    
    try:
        # Get detailed OCR data with bounding boxes
        data = pytesseract.image_to_data(
            processed_image,
            lang=lang,
            output_type=Output.DICT,
            config=config
        )
        
        logger.info(f"Enhanced OCR completed. Found {len(data['text'])} elements")
        
        # Post-process to improve confidence and text quality
        improved_data = post_process_ocr_results(data)
        
        return improved_data
        
    except Exception as e:
        logger.error(f"Enhanced OCR failed: {str(e)}")
        raise