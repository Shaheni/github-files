/**
 * ServoControls - Robot servo position control interface
 * Production-grade servo command submission with validation
 */

import React, { useState, useCallback } from 'react';
import { sendRobotCommand } from '../api/robotApi';
import { DEFAULT_ANGLES, SERVO_LIMITS } from '../constants/servoConfig';
import { validateServoValue } from '../utils/validation';
import { logger } from '../utils/logger';

/**
 * ServoControls Component
 * @param {Function} onCommandSent - callback after command submission
 * @param {boolean} disabled - disable controls
 * @param {boolean} backendOffline - backend unavailable
 */
export default function ServoControls({ onCommandSent, disabled, backendOffline }) {
  const [angles, setAngles] = useState(DEFAULT_ANGLES);
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);

  /**
   * Handle servo value change with validation
   */
  const handleChange = useCallback((idx, value) => {
    const result = validateServoValue(idx, value);
    
    if (!result.isValid) {
      setError(result.error);
      logger.debug(`Servo${idx + 1} validation error: ${result.error}`);
    } else {
      setError(null);
    }

    const intVal = parseInt(value, 10);
    const newAngles = [...angles];
    newAngles[idx] = isNaN(intVal) ? 0 : intVal;
    setAngles(newAngles);
  }, [angles]);

  /**
   * Handle command submission
   */
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();

    if (sending) {
      logger.warn('Command submission already in progress');
      return;
    }

    // Validate all servos
    for (let i = 0; i < 6; i++) {
      const result = validateServoValue(i, angles[i]);
      if (!result.isValid) {
        setError(result.error);
        return;
      }
    }

    setError(null);
    setSending(true);

    const payload = {
      servo1: angles[0],
      servo2: angles[1],
      servo3: angles[2],
      servo4: angles[3],
      servo5: angles[4],
      servo6: angles[5],
    };

    logger.info('Submitting servo command', payload);
    const res = await sendRobotCommand(payload);

    setSending(false);

    if (!res.success) {
      setError(res.error || 'Command failed');
      logger.error('Servo command failed', { error: res.error });
    } else {
      logger.info('Servo command succeeded');
    }

    if (onCommandSent) {
      onCommandSent(res);
    }
  }, [angles, sending, onCommandSent]);

  const isDisabled = disabled || backendOffline || sending || !!error;

  return (
    <form className="servo-controls" onSubmit={handleSubmit}>
      <h3>Servo Controls</h3>
      {angles.map((val, idx) => (
        <div key={idx} className="servo-row">
          <label htmlFor={`servo${idx + 1}`}>
            Servo {idx + 1} ({SERVO_LIMITS[idx].min}-{SERVO_LIMITS[idx].max}):
          </label>
          <input
            id={`servo${idx + 1}-slider`}
            type="range"
            min={SERVO_LIMITS[idx].min}
            max={SERVO_LIMITS[idx].max}
            value={val}
            disabled={isDisabled}
            onChange={e => handleChange(idx, e.target.value)}
            aria-label={`Servo ${idx + 1} slider`}
          />
          <input
            id={`servo${idx + 1}`}
            type="number"
            min={SERVO_LIMITS[idx].min}
            max={SERVO_LIMITS[idx].max}
            value={val}
            disabled={isDisabled}
            onChange={e => handleChange(idx, e.target.value)}
            aria-label={`Servo ${idx + 1} value`}
          />
        </div>
      ))}
      <button
        type="submit"
        disabled={isDisabled}
        aria-label="Send servo command"
      >
        {sending ? 'Sending...' : 'Send Command'}
      </button>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
    </form>
  );
}
