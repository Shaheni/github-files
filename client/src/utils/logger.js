/**
 * Logging utility for production debugging
 * Provides consistent logging across the application
 */

const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
};

const isDevelopment = import.meta.env.DEV;

/**
 * Format timestamp for logs
 */
function getTimestamp() {
  return new Date().toISOString();
}

/**
 * Log a message at the specified level
 */
function log(level, message, data = null) {
  const timestamp = getTimestamp();
  const logEntry = {
    timestamp,
    level,
    message,
    ...(data && { data }),
  };

  const logString = `[${timestamp}] [${level}] ${message}`;

  switch (level) {
    case LOG_LEVELS.DEBUG:
      if (isDevelopment) console.debug(logString, data);
      break;
    case LOG_LEVELS.INFO:
      console.info(logString, data);
      break;
    case LOG_LEVELS.WARN:
      console.warn(logString, data);
      break;
    case LOG_LEVELS.ERROR:
      console.error(logString, data);
      break;
    default:
      console.log(logString, data);
  }

  // In production, you could send logs to a service
  if (!isDevelopment && (level === LOG_LEVELS.ERROR || level === LOG_LEVELS.WARN)) {
    // Example: sendToLoggingService(logEntry);
  }
}

export const logger = {
  debug: (msg, data) => log(LOG_LEVELS.DEBUG, msg, data),
  info: (msg, data) => log(LOG_LEVELS.INFO, msg, data),
  warn: (msg, data) => log(LOG_LEVELS.WARN, msg, data),
  error: (msg, data) => log(LOG_LEVELS.ERROR, msg, data),
};
