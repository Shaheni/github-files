/**
 * Environment configuration
 * Loads from .env file or uses defaults
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5050';
const REQUEST_TIMEOUT_MS = import.meta.env.VITE_REQUEST_TIMEOUT || 10000;
const POLLING_INTERVAL_MS = import.meta.env.VITE_POLLING_INTERVAL || 1000;
const MAX_RETRIES = import.meta.env.VITE_MAX_RETRIES || 2;

export {
  BACKEND_URL,
  REQUEST_TIMEOUT_MS,
  POLLING_INTERVAL_MS,
  MAX_RETRIES,
};
