/**
 * EmergencyControls - Always-available emergency controls
 * STOP button and RESET button that remain functional even when robot offline
 */

import React, { useState, useCallback } from 'react';
import { emergencyStop, resetRobot } from '../api/robotApi';
import { logger } from '../utils/logger';

/**
 * EmergencyControls Component
 * @param {Function} onStop - callback after STOP
 * @param {Function} onReset - callback after RESET
 */
export default function EmergencyControls({ onStop, onReset }) {
  const [stopping, setStopping] = useState(false);
  const [resetting, setResetting] = useState(false);

  /**
   * Handle emergency stop
   */
  const handleStop = useCallback(async () => {
    if (stopping) return;
    
    setStopping(true);
    logger.warn('Emergency STOP button pressed');

    const res = await emergencyStop();

    setStopping(false);

    if (res.success) {
      logger.info('Emergency stop executed successfully');
    } else {
      logger.error('Emergency stop failed', { error: res.error });
    }

    if (onStop) onStop();
  }, [stopping, onStop]);

  /**
   * Handle reset
   */
  const handleReset = useCallback(async () => {
    if (resetting) return;

    setResetting(true);
    logger.info('Reset button pressed');

    const res = await resetRobot();

    setResetting(false);

    if (res.success) {
      logger.info('Robot reset successfully');
    } else {
      logger.error('Robot reset failed', { error: res.error });
    }

    if (onReset) onReset();
  }, [resetting, onReset]);

  return (
    <div className="emergency-controls">
      <button
        onClick={handleStop}
        disabled={stopping}
        className="btn-stop"
        aria-label="Emergency stop button - immediately stops robot motion"
        title="EMERGENCY STOP - Clears all commands"
      >
        {stopping ? 'Stopping...' : 'Emergency STOP'}
      </button>
      <button
        onClick={handleReset}
        disabled={resetting}
        className="btn-reset"
        aria-label="Reset button - resets robot to idle state"
        title="Reset - Resets motion engine to idle"
      >
        {resetting ? 'Resetting...' : 'Reset'}
      </button>
    </div>
  );
}
