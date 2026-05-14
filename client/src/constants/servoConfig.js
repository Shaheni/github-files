// CORRECTION 5: Centralized servo configuration
export const DEFAULT_ANGLES = [90, 90, 90, 90, 90, 90];

export const SERVO_LIMITS = [
  { min: 0, max: 180 },   // Servo1
  { min: 10, max: 170 },  // Servo2
  { min: 10, max: 170 },  // Servo3
  { min: 0, max: 180 },   // Servo4
  { min: 0, max: 180 },   // Servo5
  { min: 0, max: 180 },   // Servo6
];

export const MAX_QUEUE_SIZE = 3;

export const BACKEND_URL = 'http://127.0.0.1:5050';

export const POLLING_INTERVAL_MS = 1000;
