"""
Reminder Generator Module
Generates structured medication reminders from prescription data
"""

import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Khmer time slot mapping to 24-hour format
KHMER_TIME_SLOTS = {
    "ព្រឹក": {"slot": "morning", "time": "08:00", "range": "06:00-08:00"},
    "matin": {"slot": "morning", "time": "08:00", "range": "06:00-08:00"},
    "morning": {"slot": "morning", "time": "08:00", "range": "06:00-08:00"},
    
    "ថ្ងៃត្រង់": {"slot": "noon", "time": "12:00", "range": "11:00-12:00"},
    "midi": {"slot": "noon", "time": "12:00", "range": "11:00-12:00"},
    "noon": {"slot": "noon", "time": "12:00", "range": "11:00-12:00"},
    
    "ល្ងាច": {"slot": "afternoon", "time": "18:00", "range": "17:00-18:00"},
    "soir": {"slot": "afternoon", "time": "18:00", "range": "17:00-18:00"},
    "evening": {"slot": "afternoon", "time": "18:00", "range": "17:00-18:00"},
    
    "យប់": {"slot": "night", "time": "21:00", "range": "20:00-22:00"},
    "nuit": {"slot": "night", "time": "21:00", "range": "20:00-22:00"},
    "night": {"slot": "night", "time": "21:00", "range": "20:00-22:00"},
}

# Default time slots if not specified
DEFAULT_TIME_SLOTS = {
    "morning": "08:00",
    "noon": "12:00",
    "afternoon": "18:00",
    "evening": "20:00",
    "night": "21:00"
}


class ReminderGenerator:
    """Generate medication reminders from prescription data"""
    
    def __init__(self):
        self.time_slot_map = KHMER_TIME_SLOTS
        
    def generate_reminders(
        self, 
        prescription_data: Dict[str, Any],
        base_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete reminder structure from prescription data
        
        Args:
            prescription_data: Structured prescription data from AI processing
            base_date: Starting date for reminders (default: today)
            
        Returns:
            Dictionary with prescription, reminders, and metadata
        """
        try:
            # Use provided date or default to today
            from datetime import date as date_cls
            start_date = datetime.strptime(base_date, "%Y-%m-%d").date() if base_date else date_cls.today()
            
            # Extract medications
            medications = prescription_data.get("medications", [])
            patient_info = prescription_data.get("patient_info", {})
            medical_info = prescription_data.get("medical_info", {})
            
            reminders = []
            
            for med in medications:
                med_reminders = self._generate_medication_reminders(
                    med, start_date, patient_info, medical_info
                )
                reminders.extend(med_reminders)
            
            # Build complete response
            result = {
                "prescription": {
                    "patient_info": patient_info,
                    "medical_info": medical_info,
                    "medications": medications
                },
                "reminders": reminders,
                "metadata": {
                    "total_medications": len(medications),
                    "total_reminders": len(reminders),
                    "start_date": start_date.isoformat(),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            logger.info(f"Generated {len(reminders)} reminders for {len(medications)} medications")
            return result
            
        except Exception as e:
            logger.error(f"Reminder generation failed: {e}")
            return {
                "prescription": prescription_data,
                "reminders": [],
                "metadata": {
                    "error": str(e),
                    "generated_at": datetime.now().isoformat()
                }
            }
    
    def _generate_medication_reminders(
        self,
        medication: Dict[str, Any],
        start_date: date,
        patient_info: Dict[str, Any],
        medical_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate reminders for a single medication"""
        reminders = []
        
        # Extract medication details
        name = medication.get("name", "Unknown Medication")
        dosage = medication.get("dosage", "")
        quantity = medication.get("quantity", 0)
        duration_days = medication.get("duration_days")
        instructions = medication.get("instructions", "")
        
        # Get schedule information
        schedule = medication.get("schedule", {})
        times = schedule.get("times", [])
        times_24h = schedule.get("times_24h", [])
        
        # If no specific times, use default mapping
        if not times_24h and times:
            times_24h = self._convert_times_to_24h(times)
        
        # Calculate end date
        if duration_days:
            end_date = start_date + timedelta(days=duration_days)
        else:
            # Estimate from quantity if available
            daily_doses = len(times_24h) if times_24h else 1
            if quantity and daily_doses > 0:
                estimated_days = quantity // daily_doses
                end_date = start_date + timedelta(days=estimated_days)
            else:
                end_date = start_date + timedelta(days=7)  # Default 7 days
        
        # Generate reminder for each time slot
        for i, time_slot in enumerate(times):
            time_24h = times_24h[i] if i < len(times_24h) else DEFAULT_TIME_SLOTS.get(time_slot, "08:00")
            
            # Determine dose amount (default to 1)
            dose_amount = 1
            if "dose" in medication:
                dose_amount = medication.get("dose", 1)
            
            # Build notification messages
            notification_title = f"Time to take {name}"
            notification_body = self._build_notification_body(name, dosage, dose_amount, instructions)
            
            reminder = {
                "medication_name": name,
                "medication_dosage": dosage,
                "time_slot": time_slot,
                "scheduled_time": time_24h,
                "dose_amount": dose_amount,
                "dose_unit": medication.get("unit", "tablet"),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "instructions": instructions,
                "notification_title": notification_title,
                "notification_body": notification_body,
                "days_of_week": [1, 2, 3, 4, 5, 6, 7],  # All days by default
                "advance_notification_minutes": 15,
                "snooze_duration_minutes": 10
            }
            
            reminders.append(reminder)
        
        return reminders
    
    def _convert_times_to_24h(self, times: List[str]) -> List[str]:
        """Convert time slot names to 24-hour format"""
        result = []
        for time in times:
            time_lower = time.lower()
            if time_lower in self.time_slot_map:
                result.append(self.time_slot_map[time_lower]["time"])
            elif time_lower in DEFAULT_TIME_SLOTS:
                result.append(DEFAULT_TIME_SLOTS[time_lower])
            else:
                # Try to parse as time string
                result.append(time)
        return result
    
    def _build_notification_body(
        self, 
        name: str, 
        dosage: str, 
        dose_amount: int,
        instructions: str
    ) -> str:
        """Build user-friendly notification body"""
        parts = [f"Take {dose_amount} {name}"]
        
        if dosage:
            parts.append(f"({dosage})")
        
        if instructions:
            parts.append(f"- {instructions}")
        
        return " ".join(parts)
    
    def validate_reminders(self, reminders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate generated reminders for completeness and accuracy"""
        errors = []
        warnings = []
        
        for i, reminder in enumerate(reminders):
            # Check required fields
            if not reminder.get("medication_name"):
                errors.append(f"Reminder {i}: Missing medication name")
            
            if not reminder.get("scheduled_time"):
                errors.append(f"Reminder {i}: Missing scheduled time")
            
            if not reminder.get("start_date"):
                errors.append(f"Reminder {i}: Missing start date")
            
            # Validate time format
            time = reminder.get("scheduled_time", "")
            if time and not self._is_valid_time_format(time):
                warnings.append(f"Reminder {i}: Invalid time format '{time}'")
            
            # Check dose amount
            dose = reminder.get("dose_amount", 0)
            if dose <= 0:
                warnings.append(f"Reminder {i}: Invalid dose amount {dose}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_reminders": len(reminders)
        }
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in valid HH:MM format"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False


# Global instance
reminder_generator = ReminderGenerator()


def generate_reminders_from_prescription(
    prescription_data: Dict[str, Any],
    base_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function to generate reminders from prescription data
    
    Args:
        prescription_data: Structured prescription data
        base_date: Optional start date (YYYY-MM-DD)
        
    Returns:
        Complete reminder structure with validation
    """
    result = reminder_generator.generate_reminders(prescription_data, base_date)
    
    # Validate the generated reminders
    validation = reminder_generator.validate_reminders(result.get("reminders", []))
    result["validation"] = validation
    
    return result
