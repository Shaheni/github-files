/**
 * Input validation utilities
 */

import { SERVO_LIMITS } from '../constants/servoConfig';

/**
 * Validate a single servo value
 * @param {number} servoIndex - 0-5
 * @param {number} value - angle value
 * @returns {Object} { isValid: boolean, error?: string }
 */
export function validateServoValue(servoIndex, value) {
  if (servoIndex < 0 || servoIndex > 5) {
    return { isValid: false, error: 'Invalid servo index' };
  }

  const intValue = parseInt(value, 10);
  if (isNaN(intValue)) {
    return { isValid: false, error: `Servo${servoIndex + 1} must be a number` };
  }

  const { min, max } = SERVO_LIMITS[servoIndex];
  if (intValue < min || intValue > max) {
    return { isValid: false, error: `Servo${servoIndex + 1} must be ${min}-${max}` };
  }

  return { isValid: true };
}

/**
 * Validate all servo values
 * @param {Array<number>} angles - array of 6 angle values
 * @returns {Object} { isValid: boolean, errors: Array<string> }
 */
export function validateAllServos(angles) {
  const errors = [];

  if (!Array.isArray(angles) || angles.length !== 6) {
    return { isValid: false, errors: ['Must provide exactly 6 servo angles'] };
  }

  for (let i = 0; i < 6; i++) {
    const result = validateServoValue(i, angles[i]);
    if (!result.isValid) {
      errors.push(result.error);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Sanitize servo angles to valid range
 * @param {Array<number>} angles
 * @returns {Array<number>} clipped angles
 */
export function sanitizeServoAngles(angles) {
  return angles.map((angle, idx) => {
    const { min, max } = SERVO_LIMITS[idx];
    return Math.max(min, Math.min(max, parseInt(angle, 10)));
  });
}
