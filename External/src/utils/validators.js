/**
 * Form field validation utilities
 */

export function validateRequired(value, fieldName = 'This field') {
  if (!value || (typeof value === 'string' && value.trim().length === 0)) {
    return `${fieldName} is required`;
  }
  return null;
}

export function validateEmail(email) {
  if (!email || !email.trim()) {
    return 'Email address is required';
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.trim())) {
    return 'Please enter a valid email address';
  }
  return null;
}

export function validatePhone(phone) {
  if (!phone || !phone.trim()) {
    return 'Phone number is required';
  }
  const phoneRegex = /^[+\d][\d\s\-().]{6,}$/;
  if (!phoneRegex.test(phone.trim())) {
    return 'Please enter a valid phone number (min 7 digits)';
  }
  return null;
}

export function validateMinLength(value, min = 10, fieldName = 'Message') {
  if (!value || value.trim().length < min) {
    return `${fieldName} must be at least ${min} characters`;
  }
  return null;
}

