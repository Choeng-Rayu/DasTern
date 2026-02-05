"""
Structured Data Extraction for Medical Prescriptions
Extracts medication, patient info, doctor info, dates, and dosage information
"""
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from ...core.logger import logger


# Khmer medical terms dictionary
KHMER_MEDICAL_TERMS = {
    # Time of day
    'ព្រឹក': 'morning',
    'រសៀល': 'afternoon',
    'ល្ងាច': 'evening',
    'យប់': 'night',
    'ថ្ងៃ': 'day',
    
    # Administration
    'លេប': 'oral',
    'ញ៉ាំ': 'eat/take',
    'ផឹក': 'drink',
    'ចាក់': 'inject',
    'លាប': 'apply',
    
    # Units
    'គ្រាប់': 'tablet/pill',
    'ស្លាបព្រាកាហ្វេ': 'teaspoon',
    'ស្លាបព្រាស៊ុប': 'tablespoon',
    'មីលីក្រាម': 'milligram',
    'ក្រាម': 'gram',
    
    # Frequency
    'ម្ដង': 'times',
    'ដង': 'times',
    'ជារៀងរាល់': 'every',
    'មុន': 'before',
    'ក្រោយ': 'after',
    'អាហារ': 'meal',
    
    # Medical roles
    'គ្រូពេទ្យ': 'doctor',
    'ពេទ្យ': 'doctor',
    'អ្នកជំងឺ': 'patient',
    'មន្ទីរពេទ្យ': 'hospital',
    'គ្លីនិក': 'clinic',
}


# Common medication name patterns
MEDICATION_PATTERNS = [
    # Generic medicine names (case-insensitive)
    r'\b(paracetamol|acetaminophen|tylenol)\b',
    r'\b(amoxicillin|amoxil)\b',
    r'\b(ibuprofen|advil|motrin)\b',
    r'\b(metformin)\b',
    r'\b(omeprazole|prilosec)\b',
    r'\b(losartan)\b',
    r'\b(atorvastatin|lipitor)\b',
    r'\b(amlodipine|norvasc)\b',
    r'\b(ciprofloxacin|cipro)\b',
    r'\b(azithromycin|zithromax)\b',
    r'\b(prednisone)\b',
    r'\b(insulin)\b',
    r'\b(glibenclamide|glyburide)\b',
    r'\b(multivitamine?|vitamin)\b',
    r'\b(calcium)\b',
    r'\b(celcoxx|celebrex)\b',
    r'\b(butylscopolamine|buscopan)\b',
    r'\b(amitriptyline)\b',
    
    # Pattern for medicine with dosage
    r'\b([A-Z][a-z]+[A-Z]?[a-z]*)\s*\d+\s*(mg|g|ml)\b',
]


# Dosage patterns
DOSAGE_PATTERNS = [
    # Number + unit
    r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|µg|iu)',
    r'(\d+)\s*(tablet|pill|capsule|cap|tab)',
    
    # Khmer dosage
    r'(\d+)\s*គ្រាប់',  # tablets in Khmer
    r'(\d+)\s*ស្លាបព្រា',  # spoons in Khmer
]


# Frequency patterns
FREQUENCY_PATTERNS = [
    # Standard medical abbreviations
    r'\b(\d+)\s*x\s*/?\s*day\b',
    r'\b(\d+)\s*times?\s*(?:per|a)\s*day\b',
    r'\bonce\s*(?:a|per)\s*day\b',
    r'\btwice\s*(?:a|per)\s*day\b',
    r'\bthree\s*times?\s*(?:a|per)\s*day\b',
    r'\bevery\s*(\d+)\s*hours?\b',
    
    # Times per day with numbers
    r'(\d+)x/day',
    r'(\d+)x\s*(?:per|a)\s*day',
    
    # Khmer frequency
    r'(\d+)\s*ដង\s*ក្នុង\s*1\s*ថ្ងៃ',  # X times per day
    r'(\d+)\s*ដង/ថ្ងៃ',  # X times/day
]


# Date patterns (multiple formats)
DATE_PATTERNS = [
    # DD/MM/YYYY or DD-MM-YYYY
    r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
    # YYYY/MM/DD or YYYY-MM-DD
    r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
    # DD/MM/YY
    r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})\b',
    # Khmer date format
    r'(\d{1,2})\s*ខែ\s*(\d{1,2})\s*ឆ្នាំ\s*(\d{4})',
]


# Time patterns
TIME_PATTERNS = [
    # HH:MM format
    r'(\d{1,2}):(\d{2})',
    # Khmer time
    r'ម៉ោង\s*(\d{1,2})',
]


def extract_medications(text: str, ocr_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract medication names from text and OCR data
    
    Args:
        text: Full OCR text
        ocr_data: Raw OCR data with bounding boxes
        
    Returns:
        List of medications with details
    """
    medications = []
    text_lower = text.lower()
    
    # Search for medication patterns
    for pattern in MEDICATION_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            med_name = match.group(0)
            
            # Find dosage near medication name
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 50)
            context = text[context_start:context_end]
            
            dosage = extract_dosage_from_context(context)
            frequency = extract_frequency_from_context(context)
            
            medications.append({
                "name": med_name.strip(),
                "dosage": dosage,
                "frequency": frequency,
                "position": match.start()
            })
    
    # Remove duplicates
    seen = set()
    unique_meds = []
    for med in medications:
        key = med['name'].lower()
        if key not in seen:
            seen.add(key)
            unique_meds.append(med)
    
    logger.info(f"Extracted {len(unique_meds)} medications")
    
    return unique_meds


def extract_dosage_from_context(text: str) -> Optional[str]:
    """Extract dosage information from context"""
    for pattern in DOSAGE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def extract_frequency_from_context(text: str) -> Optional[str]:
    """Extract frequency information from context"""
    for pattern in FREQUENCY_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def extract_patient_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract patient information from text
    
    Args:
        text: OCR text
        
    Returns:
        Dictionary with patient details
    """
    patient_info = {
        "name": None,
        "id": None,
        "age": None,
        "gender": None
    }
    
    # Patient name patterns
    name_patterns = [
        r'(?:patient|name|អ្នកជំងឺ|ឈ្មោះ)[:\s]+([A-Za-zក-អ\s]+)',
        r'(?:mr\.|mrs\.|ms\.)\s+([A-Za-z\s]+)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_info["name"] = match.group(1).strip()
            break
    
    # Patient ID patterns
    id_patterns = [
        r'(?:patient\s*id|id|លេខអត្តសញ្ញាណ)[:\s]+([A-Z0-9\-/]+)',
        r'\b([A-Z]+\d{6,})\b',  # Pattern like HAKF1354164
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_info["id"] = match.group(1).strip()
            break
    
    # Age patterns
    age_patterns = [
        r'(?:age|อายุ|អាយុ)[:\s]+(\d+)',
        r'(\d+)\s*(?:years?|y\.?o\.?|ឆ្នាំ)',
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_info["age"] = match.group(1).strip()
            break
    
    # Gender patterns
    gender_patterns = [
        r'\b(male|female|m|f|ប្រុស|ស្រី)\b',
    ]
    
    for pattern in gender_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            gender = match.group(1).lower()
            if gender in ['male', 'm', 'ប្រុស']:
                patient_info["gender"] = "male"
            elif gender in ['female', 'f', 'ស្រី']:
                patient_info["gender"] = "female"
            break
    
    return patient_info


def extract_doctor_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract doctor information from text
    
    Args:
        text: OCR text
        
    Returns:
        Dictionary with doctor details
    """
    doctor_info = {
        "name": None,
        "signature": False
    }
    
    # Doctor name patterns
    doctor_patterns = [
        r'(?:dr\.|doctor|គ្រូពេទ្យ|ពេទ្យ)[:\s]+([A-Za-zក-អ\s]+)',
        r'(?:physician|prescriber)[:\s]+([A-Za-z\s]+)',
    ]
    
    for pattern in doctor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doctor_info["name"] = match.group(1).strip()
            break
    
    # Check for signature indicators
    if re.search(r'(signature|signed|ហត្ថលេខា)', text, re.IGNORECASE):
        doctor_info["signature"] = True
    
    return doctor_info


def extract_dates(text: str) -> List[Dict[str, Any]]:
    """
    Extract dates from text
    
    Args:
        text: OCR text
        
    Returns:
        List of dates with context
    """
    dates = []
    
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            date_str = match.group(0)
            
            # Try to parse the date
            parsed_date = parse_date(date_str)
            
            # Get context
            context_start = max(0, match.start() - 30)
            context_end = min(len(text), match.end() + 30)
            context = text[context_start:context_end]
            
            dates.append({
                "date_string": date_str,
                "parsed_date": parsed_date,
                "context": context.strip()
            })
    
    return dates


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse date string to ISO format
    
    Args:
        date_str: Date string
        
    Returns:
        ISO format date string or None
    """
    # Try common date formats
    formats = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%Y-%m-%d',
        '%d/%m/%y',
        '%d-%m-%y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None


def extract_times(text: str) -> List[str]:
    """
    Extract time information
    
    Args:
        text: OCR text
        
    Returns:
        List of time strings
    """
    times = []
    
    for pattern in TIME_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            times.append(match.group(0))
    
    return times


def extract_time_of_day(text: str) -> List[str]:
    """
    Extract time of day (morning, afternoon, evening, night)
    
    Args:
        text: OCR text
        
    Returns:
        List of time of day indicators
    """
    time_of_day = []
    
    # English patterns
    english_times = ['morning', 'afternoon', 'evening', 'night', 'bedtime']
    for time in english_times:
        if re.search(rf'\b{time}\b', text, re.IGNORECASE):
            time_of_day.append(time)
    
    # Khmer patterns
    for khmer_time, english_time in KHMER_MEDICAL_TERMS.items():
        if english_time in ['morning', 'afternoon', 'evening', 'night']:
            if khmer_time in text:
                time_of_day.append(english_time)
    
    return list(set(time_of_day))


def extract_structured_data(
    text: str,
    ocr_data: List[Dict[str, Any]],
    table_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract all structured data from prescription
    
    Args:
        text: Full OCR text
        ocr_data: Raw OCR data with bounding boxes
        table_data: Optional table structure data
        
    Returns:
        Comprehensive structured data
    """
    logger.info("Extracting structured prescription data")
    
    structured = {
        "patient": extract_patient_info(text),
        "doctor": extract_doctor_info(text),
        "medications": extract_medications(text, ocr_data),
        "dates": extract_dates(text),
        "times": extract_times(text),
        "time_of_day": extract_time_of_day(text),
        "table_detected": table_data is not None if table_data else False
    }
    
    # Enhance with table data if available
    if table_data and table_data.get('found_table'):
        structured["table_medications"] = extract_medications_from_table(table_data)
    
    logger.info(f"Extracted structured data: {len(structured['medications'])} medications, "
                f"{len(structured['dates'])} dates")
    
    return structured


def extract_medications_from_table(table_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract medication information from table structure
    
    Args:
        table_data: Table structure data
        
    Returns:
        List of medications extracted from table
    """
    medications = []
    
    if not table_data.get('table_grid'):
        return medications
    
    table_grid = table_data['table_grid']
    
    # Skip header row (usually first row)
    for row_idx, row in enumerate(table_grid[1:], start=1):
        if not row:
            continue
        
        # Try to extract medication name (usually first column)
        med_name = row[0].get('text', '').strip() if len(row) > 0 else ''
        
        if not med_name:
            continue
        
        # Extract other details from row
        dosage = row[1].get('text', '').strip() if len(row) > 1 else ''
        frequency = row[2].get('text', '').strip() if len(row) > 2 else ''
        
        medications.append({
            "name": med_name,
            "dosage": dosage,
            "frequency": frequency,
            "row": row_idx,
            "source": "table"
        })
    
    return medications
