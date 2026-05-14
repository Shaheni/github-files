/**
 * StatusPanel - Display robot motion status
 * Shows execution state, queue size, last command, and errors
 */

import React, { useMemo } from 'react';

/**
 * StatusPanel Component
 * @param {Object} motion - motion data from /api/robot/status
 * @param {boolean} loading - loading state
 */
export default function StatusPanel({ motion, loading }) {
  const displayState = useMemo(() => {
    if (loading) {
      return {
        display: 'Checking robot state...',
        isLoading: true,
      };
    }

    if (!motion) {
      return {
        display: 'Loading status...',
        isLoading: true,
      };
    }

    return {
      display: null,
      isLoading: false,
      state: motion.state,
      queueSize: motion.queue_size,
      maxQueue: motion.max_queue_size,
      lastCommand: motion.last_command,
      lastError: motion.last_error,
    };
  }, [motion, loading]);

  if (displayState.isLoading) {
    return (
      <div className="status-panel">
        <h3>Status</h3>
        <div className="loading">{displayState.display}</div>
      </div>
    );
  }

  return (
    <div className="status-panel">
      <h3>Status</h3>
      <div>
        <b>Execution State:</b>{' '}
        <span className={`state-${displayState.state}`}>
          {displayState.state}
        </span>
      </div>
      <div>
        <b>Queue Size:</b> {displayState.queueSize} / {displayState.maxQueue}
      </div>
      <div>
        <b>Last Command:</b> {displayState.lastCommand || '-'}
      </div>
      <div>
        <b>Last Error:</b>{' '}
        <span className="error">{displayState.lastError || '-'}</span>
      </div>
    </div>
  );
}
