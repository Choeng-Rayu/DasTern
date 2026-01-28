#!/usr/bin/env python3
"""
Enhanced prescription parser for Khmer prescriptions
Handles the specific table format with timing columns
"""

import re
import json
from typing import List, Dict, Any

class KhmerPrescriptionParser:
    """Parser for Khmer prescription format"""
    
    def __init__(self):
        # Common medication names found in Khmer prescriptions
        self.known_medications = [
            'Calcium', 'Multivitamine', 'Amitriptyline', 'Butylscopolamine',
            'Celcoxx', 'Omeprazole', 'Paracetamol', 'Esome', 'Multivitamine'
        ]
        
        # Khmer time indicators
        self.time_indicators = {
            'ព្រឹក': 'morning',    # Morning
            'ថ្ងៃ': 'noon',        # Noon/Day
            'ល្ងាច': 'evening',    # Evening
            'យប់': 'night'         # Night
        }
    
    def parse_prescription_table(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse the prescription table format:
        លេខ ឈ្មោះថ្នាំ ចំនួន ព្រឹក ថ្ងៃ ល្ងាច យប់ សម្គាល់ ថ្ងៃ
        1. Calcium amp Tablet 1 - - - ថ្នាំបញ្ចុះ 4
        """
        medications = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Look for numbered medication lines
            if re.match(r'^\d+\.', line):
                med_info = self._parse_medication_line(line)
                if med_info:
                    medications.append(med_info)
        
        return medications if medications else self._create_fallback_medications(text)
    
    def _parse_medication_line(self, line: str) -> Dict[str, Any]:
        """Parse a single medication line from the table"""
        
        # Split the line into parts
        parts = line.split()
        if len(parts) < 4:
            return None
        
        # Extract medication name (usually after the number)
        med_name = None
        for part in parts[1:]:  # Skip the number
            if any(known_med.lower() in part.lower() for known_med in self.known_medications):
                med_name = part
                break
        
        if not med_name:
            # Try to find any medication-like word
            for part in parts[1:4]:  # Check first few parts
                if re.match(r'^[A-Za-z]+', part) and len(part) > 3:
                    med_name = part
                    break
        
        if not med_name:
            return None
        
        # Extract strength (e.g., "10mg")
        strength = None
        strength_match = re.search(r'(\d+)\s*(mg|ml)', line, re.IGNORECASE)
        if strength_match:
            strength = strength_match.group(0)
        
        # Extract dosage from quantity column
        dosage = "1 tablet"  # Default
        quantity_match = re.search(r'(\d+)\s*(tablet|ថ្នាំ)', line, re.IGNORECASE)
        if quantity_match:
            dosage = f"{quantity_match.group(1)} tablet"
        
        # Parse timing columns (ព្រឹក ថ្ងៃ ល្ងាច យប់)
        timing_info = self._parse_timing_columns(line)
        
        # Extract duration (last number in the line)
        duration_match = re.search(r'(\d+)\s*$', line)
        duration = f"{duration_match.group(1)} days" if duration_match else "7 days"
        
        return {
            'name': med_name,
            'strength': strength,
            'dosage': dosage,
            'timing': timing_info,
            'frequency': self._timing_to_frequency(timing_info),
            'duration': duration,
            'instructions': 'Take as prescribed',
            'raw_line': line
        }
    
    def _parse_timing_columns(self, line: str) -> Dict[str, bool]:
        """
        Parse the timing columns: ព្រឹក ថ្ងៃ ល្ងាច យប់
        Look for numbers (1) or dashes (-) in each column
        """
        timing = {
            'morning': False,
            'noon': False, 
            'evening': False,
            'night': False
        }
        
        # Split line and look for timing indicators
        parts = line.split()
        
        # Find timing pattern: look for sequences of numbers and dashes
        # Example: "1 - - -" or "1 - 1 -" or "- - - 1"
        timing_pattern = re.findall(r'[1-9-]', line)
        
        if len(timing_pattern) >= 4:
            # Map to timing slots
            timing['morning'] = timing_pattern[0] != '-' and timing_pattern[0].isdigit()
            timing['noon'] = timing_pattern[1] != '-' and timing_pattern[1].isdigit()
            timing['evening'] = timing_pattern[2] != '-' and timing_pattern[2].isdigit()
            timing['night'] = timing_pattern[3] != '-' and timing_pattern[3].isdigit()
        
        return timing
    
    def _timing_to_frequency(self, timing: Dict[str, bool]) -> str:
        """Convert timing info to frequency description"""
        active_times = sum(timing.values())
        
        if active_times == 0:
            return "once daily"
        elif active_times == 1:
            return "once daily"
        elif active_times == 2:
            return "twice daily"
        elif active_times == 3:
            return "three times daily"
        elif active_times == 4:
            return "four times daily"
        else:
            return "as prescribed"
    
    def _create_fallback_medications(self, text: str) -> List[Dict[str, Any]]:
        """Create fallback medications if parsing fails"""
        medications = []
        
        # Look for any medication names in the text
        for med_name in self.known_medications:
            if med_name.lower() in text.lower():
                medications.append({
                    'name': med_name,
                    'strength': None,
                    'dosage': '1 tablet',
                    'timing': {'morning': True, 'noon': False, 'evening': False, 'night': False},
                    'frequency': 'once daily',
                    'duration': '7 days',
                    'instructions': 'Take as prescribed',
                    'raw_line': f'Found: {med_name}'
                })
        
        # If still no medications, create a placeholder
        if not medications:
            medications.append({
                'name': 'Unknown Medication',
                'strength': None,
                'dosage': '1 tablet',
                'timing': {'morning': True, 'noon': False, 'evening': False, 'night': False},
                'frequency': 'once daily',
                'duration': '7 days',
                'instructions': 'Please review prescription manually',
                'raw_line': 'Fallback medication'
            })
        
        return medications
    
    def generate_reminders(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate reminder schedule from parsed medications"""
        reminders = []
        
        for med in medications:
            timing = med.get('timing', {})
            reminder_times = []
            
            # Convert timing to specific times
            if timing.get('morning'):
                reminder_times.append('08:00')
            if timing.get('noon'):
                reminder_times.append('12:00')
            if timing.get('evening'):
                reminder_times.append('18:00')
            if timing.get('night'):
                reminder_times.append('22:00')
            
            # Default to morning if no times specified
            if not reminder_times:
                reminder_times = ['08:00']
            
            # Extract duration in days
            duration_str = med.get('duration', '7 days')
            duration_match = re.search(r'(\d+)', duration_str)
            duration_days = int(duration_match.group(1)) if duration_match else 7
            
            reminder = {
                'medication_name': med['name'],
                'strength': med['strength'],
                'dosage': med['dosage'],
                'reminder_times': reminder_times,
                'days_of_week': [1, 2, 3, 4, 5, 6, 7],  # All days
                'duration_days': duration_days,
                'instructions': med['instructions'],
                'timing_details': timing
            }
            
            reminders.append(reminder)
        
        return reminders

def test_enhanced_parser():
    """Test the enhanced parser with sample data"""
    
    # Sample OCR text from your prescription images
    sample_texts = [
        # First prescription
        """
        SOK HENG POLYCLINIC
        តេជោបញ្ញា
        
        ឈ្មោះ: ឈុន ចាប់ ភេទ: ស្រី អាយុ: 47 ឆ្នាំ
        
        លេខ ឈ្មោះថ្នាំ ចំនួន ព្រឹក ថ្ងៃ ល្ងាច យប់ សម្គាល់ ថ្ងៃ
        1. Calcium amp Tablet 1 - - - ថ្នាំបញ្ចុះ 4
        2. Multivitamine Tablet 1 - 1 - ថ្នាំបញ្ចុះ 10
        3. Amitriptyline 10mg - - - 1 ថ្នាំបញ្ចុះ 5
        """,
        
        # Second prescription
        """
        H-EQIP
        HAKF1354164
        
        លេខ ឈ្មោះថ្នាំ ចំនួន ព្រឹក ថ្ងៃ ល្ងាច យប់
        1 Butylscopolamine 10mg 14 ថ្នាំ 1 - 1 -
        2 Multivitamine 10 ថ្នាំ 1 - 1 -
        3 Esome 20mg 7 ថ្នាំបញ្ចុះ PO ថ្នាំ បញ្ចុះបញ្ចុះ - -
        4 Paracetamol 500mg 15 ថ្នាំ PO ថ្នាំ បញ្ចុះបញ្ចុះ ថ្នាំ បញ្ចុះបញ្ចុះ -
        """,
        
        # Third prescription
        """
        H-EQIP
        HAKF1354164
        
        លេខ ឈ្មោះថ្នាំ ចំនួន ព្រឹក ថ្ងៃ ល្ងាច យប់
        1 Butylscopolamine 10mg 14 ថ្នាំ 1 - 1 -
        2 Celcoxx 100mg 14 ថ្នាំបញ្ចុះ 1 - 1 -
        3 Omeprazole 20mg 14 ថ្នាំ 1 - 1 -
        4 Multivitamine 21 ថ្នាំ 1 1 1 -
        """
    ]
    
    parser = KhmerPrescriptionParser()
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n{'='*60}")
        print(f"🏥 Testing Prescription {i}")
        print(f"{'='*60}")
        
        # Parse medications
        medications = parser.parse_prescription_table(text)
        print(f"💊 Found {len(medications)} medications:")
        
        for j, med in enumerate(medications, 1):
            print(f"  {j}. {med['name']}")
            print(f"     Strength: {med['strength']}")
            print(f"     Dosage: {med['dosage']}")
            print(f"     Timing: {med['timing']}")
            print(f"     Frequency: {med['frequency']}")
            print(f"     Duration: {med['duration']}")
            print()
        
        # Generate reminders
        reminders = parser.generate_reminders(medications)
        print(f"⏰ Generated {len(reminders)} reminders:")
        
        for j, reminder in enumerate(reminders, 1):
            print(f"  {j}. {reminder['medication_name']}")
            print(f"     Times: {', '.join(reminder['reminder_times'])}")
            print(f"     Duration: {reminder['duration_days']} days")
            print()
        
        # Save results
        results = {
            'prescription_id': f'test_{i}',
            'ocr_text': text.strip(),
            'medications': medications,
            'reminders': reminders,
            'timestamp': '2026-01-23T10:00:00Z'
        }
        
        with open(f'prescription_test_{i}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to prescription_test_{i}.json")

if __name__ == "__main__":
    test_enhanced_parser()