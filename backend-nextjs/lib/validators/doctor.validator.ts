import { ValidationResult } from './auth.validator';

export function validateDoctorProfile(data: any): ValidationResult {
  const errors: Record<string, string> = {};

  // License number
  if (!data.license_number) {
    errors.license_number = 'Medical license number is required';
  } else if (data.license_number.length < 5) {
    errors.license_number = 'Invalid license number format';
  }

  // Specialization
  if (!data.specialization) {
    errors.specialization = 'Specialization is required';
  }

  // Hospital name
  if (!data.hospital_name) {
    errors.hospital_name = 'Hospital/clinic name is required';
  }

  // Years of experience
  if (data.years_of_experience === undefined || data.years_of_experience === null) {
    errors.years_of_experience = 'Years of experience is required';
  } else if (data.years_of_experience < 0 || data.years_of_experience > 70) {
    errors.years_of_experience = 'Invalid years of experience';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}