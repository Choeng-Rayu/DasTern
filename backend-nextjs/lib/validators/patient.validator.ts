import { ValidationResult } from './auth.validator';

export function validatePatientProfile(data: any): ValidationResult {
  const errors: Record<string, string> = {};

  // Meal schedule validation
  if (!data.meal_schedule) {
    errors.meal_schedule = 'Meal schedule is required';
  } else {
    const { morning, noon, evening, night } = data.meal_schedule;
    const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;

    if (!morning || !timeRegex.test(morning)) {
      errors['meal_schedule.morning'] = 'Valid morning time required (HH:MM)';
    }
    if (!noon || !timeRegex.test(noon)) {
      errors['meal_schedule.noon'] = 'Valid noon time required (HH:MM)';
    }
    if (!evening || !timeRegex.test(evening)) {
      errors['meal_schedule.evening'] = 'Valid evening time required (HH:MM)';
    }
    if (!night || !timeRegex.test(night)) {
      errors['meal_schedule.night'] = 'Valid night time required (HH:MM)';
    }
  }

  // Emergency contact validation
  if (!data.emergency_contact_name) {
    errors.emergency_contact_name = 'Emergency contact name is required';
  }

  if (!data.emergency_contact_phone) {
    errors.emergency_contact_phone = 'Emergency contact phone is required';
  } else if (!/^\+?[1-9]\d{8,14}$/.test(data.emergency_contact_phone)) {
    errors.emergency_contact_phone = 'Invalid phone format';
  }

  // Optional fields validation
  if (data.blood_type) {
    const validBloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
    if (!validBloodTypes.includes(data.blood_type)) {
      errors.blood_type = 'Invalid blood type';
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}