/**
 * Backend API client with error handling, retries, and timeouts
 * Production-grade API communication layer
 */

import axios from 'axios';
import { BACKEND_URL, REQUEST_TIMEOUT_MS, MAX_RETRIES } from '../config/env';
import { logger } from '../utils/logger';

/**
 * Create axios instance with timeout and other production settings
 */
const apiClient = axios.create({
  baseURL: BACKEND_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Normalize API errors to consistent format
 * @param {Error} err - axios error
 * @param {string} operation - operation name for logging
 * @returns {Object} normalized error object
 */
function normalizeError(err, operation = 'api_call') {
  logger.error(`API error in ${operation}`, {
    message: err.message,
    status: err.response?.status,
    data: err.response?.data,
  });

  // Network/timeout error - backend offline
  if (!err.response || err.code === 'ECONNABORTED') {
    return {
      success: false,
      type: 'backend_offline',
      error: 'Backend unavailable - check server connection',
    };
  }

  // HTTP status-based error mapping
  if (err.response.status === 400) {
    return {
      success: false,
      type: 'validation',
      error: err.response.data?.error || 'Validation error',
    };
  }

  if (err.response.status === 429) {
    return {
      success: false,
      type: 'queue_full',
      error: err.response.data?.error || 'Queue full',
    };
  }

  if (err.response.status === 500) {
    return {
      success: false,
      type: 'hardware',
      error: err.response.data?.error || 'Hardware communication error',
    };
  }

  if (err.response.status === 503) {
    return {
      success: false,
      type: 'backend_offline',
      error: 'Backend service unavailable',
    };
  }

  return {
    success: false,
    type: 'unknown',
    error: 'Unexpected error',
  };
}

/**
 * Retry logic with exponential backoff
 * @param {Function} fn - async function to retry
 * @param {number} maxRetries - max retry attempts
 * @returns {Promise} result
 */
async function withRetry(fn, maxRetries = MAX_RETRIES) {
  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;

      // Don't retry validation errors
      if (err.response?.status === 400) {
        throw err;
      }

      // Exponential backoff: 100ms, 300ms, 900ms
      if (attempt < maxRetries) {
        const delay = Math.pow(3, attempt) * 100;
        logger.debug(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}


/**
 * Send robot motion command
 * @param {Object} angles - servo angles { servo1, servo2, ..., servo6 }
 * @returns {Promise<Object>} response with success flag
 */
export async function sendRobotCommand(angles) {
  try {
    const result = await withRetry(() =>
      apiClient.post('/api/robot/command', angles)
    );
    logger.info('Robot command sent successfully', { angles });
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'sendRobotCommand');
  }
}

/**
 * Get current robot status
 * @returns {Promise<Object>} robot status
 */
export async function getRobotStatus() {
  try {
    const result = await withRetry(() =>
      apiClient.get('/api/robot/status')
    );
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'getRobotStatus');
  }
}

/**
 * Get telemetry data
 * @returns {Promise<Object>} telemetry data
 */
export async function getTelemetry() {
  try {
    const result = await withRetry(() =>
      apiClient.get('/api/telemetry')
    );
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'getTelemetry');
  }
}

/**
 * Check backend health and Arduino connection
 * @returns {Promise<Object>} health status
 */
export async function healthCheck() {
  try {
    const result = await withRetry(() =>
      apiClient.get('/api/health')
    );
    logger.debug('Health check passed', result.data);
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'healthCheck');
  }
}

/**
 * Emergency stop - clear command queue
 * @returns {Promise<Object>} response
 */
export async function emergencyStop() {
  try {
    logger.warn('EMERGENCY STOP activated');
    const result = await apiClient.post('/api/robot/stop');
    logger.info('Emergency stop executed');
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'emergencyStop');
  }
}

/**
 * Reset motion engine to idle state
 * @returns {Promise<Object>} response
 */
export async function resetRobot() {
  try {
    logger.info('Resetting robot');
    const result = await apiClient.post('/api/robot/reset');
    logger.info('Robot reset successfully');
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'resetRobot');
  }
}

/**
 * Get camera status
 * @returns {Promise<Object>} camera status
 */
export async function getCameraStatus() {
  try {
    const result = await withRetry(() =>
      apiClient.get('/api/camera/status')
    );
    logger.debug('Camera status retrieved', result.data);
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'getCameraStatus');
  }
}

/**
 * Start camera capture
 * @returns {Promise<Object>} response
 */
export async function startCamera() {
  try {
    logger.info('Starting camera...');
    const result = await apiClient.post('/api/camera/start');
    logger.info('Camera started');
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'startCamera');
  }
}

/**
 * Stop camera capture
 * @returns {Promise<Object>} response
 */
export async function stopCamera() {
  try {
    logger.info('Stopping camera...');
    const result = await apiClient.post('/api/camera/stop');
    logger.info('Camera stopped');
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'stopCamera');
  }
}

/**
 * Get voice recognition status
 * @returns {Promise<Object>} voice status
 */
export async function getVoiceStatus() {
  try {
    const result = await withRetry(() =>
      apiClient.get('/api/voice/status')
    );
    logger.debug('Voice status retrieved', { queue_size: result.data.queue_size });
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'getVoiceStatus');
  }
}

/**
 * Start voice recognition
 * @returns {Promise<Object>} response
 */
export async function startVoice() {
  try {
    logger.info('Starting voice recognition...');
    const result = await apiClient.post('/api/voice/start');
    logger.info('Voice recognition started');
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'startVoice');
  }
}

/**
 * Stop voice recognition
 * @returns {Promise<Object>} response
 */
export async function stopVoice() {
  try {
    logger.info('Stopping voice recognition...');
    const result = await apiClient.post('/api/voice/stop');
    logger.info('Voice recognition stopped');
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'stopVoice');
  }
}

/**
 * Get next voice command from queue
 * @returns {Promise<Object>} command or empty
 */
export async function getVoiceCommand() {
  try {
    const result = await apiClient.get('/api/voice/command/next');
    if (result.status === 204) {
      return { command: null, type: 'success' };
    }
    logger.debug('Voice command retrieved', result.data.command?.text);
    return { ...result.data, type: 'success' };
  } catch (err) {
    // 204 is expected when no commands
    if (err.response?.status === 204) {
      return { command: null, type: 'success' };
    }
    return normalizeError(err, 'getVoiceCommand');
  }
}
