export interface ValidationResult {
  valid: boolean;
  errors: Record<string, string>;
}

export function validateRegister(data: any): ValidationResult {
  const errors: Record<string, string> = {};

  // Email
  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(data.email)) {
    errors.email = 'Invalid email format';
  }

  // Password
  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
    errors.password = 'Password must contain uppercase, lowercase, and number';
  }

  // First name
  if (!data.first_name) {
    errors.first_name = 'First name is required';
  } else if (data.first_name.length < 2) {
    errors.first_name = 'First name must be at least 2 characters';
  }

  // Last name
  if (!data.last_name) {
    errors.last_name = 'Last name is required';
  } else if (data.last_name.length < 2) {
    errors.last_name = 'Last name must be at least 2 characters';
  }

  // Phone
  if (!data.telephone) {
    errors.telephone = 'Phone number is required';
  } else if (!/^\+?[1-9]\d{8,14}$/.test(data.telephone)) {
    errors.telephone = 'Invalid phone format. Use international format: +855123456789';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}

export function validateLogin(data: any): ValidationResult {
  const errors: Record<string, string> = {};

  if (!data.email) {
    errors.email = 'Email or phone is required';
  }

  if (!data.password) {
    errors.password = 'Password is required';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}

export function validateRoleSelection(data: any): ValidationResult {
  const errors: Record<string, string> = {};
  const validRoles = ['patient', 'doctor', 'family_member'];

  if (!data.role) {
    errors.role = 'Role is required';
  } else if (!validRoles.includes(data.role)) {
    errors.role = `Invalid role. Must be one of: ${validRoles.join(', ')}`;
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}