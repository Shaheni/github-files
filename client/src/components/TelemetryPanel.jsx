/**
 * TelemetryPanel - Display real robot telemetry data
 * Shows serial status, Arduino response, execution state, and errors
 * Only displays REAL runtime state (no fake telemetry)
 */

import React, { useMemo } from 'react';

/**
 * TelemetryPanel Component
 * @param {Object} telemetry - telemetry data from /api/telemetry
 * @param {boolean} loading - loading state
 */
export default function TelemetryPanel({ telemetry, loading }) {
  const displayState = useMemo(() => {
    if (loading) {
      return {
        display: 'Fetching telemetry...',
        isLoading: true,
      };
    }

    if (!telemetry) {
      return {
        display: 'Loading telemetry...',
        isLoading: true,
      };
    }

    return {
      display: null,
      isLoading: false,
      serialConnected: telemetry.serial_connected,
      serialPort: telemetry.serial_port,
      lastArduinoResponse: telemetry.last_arduino_response,
      executionState: telemetry.execution_state,
      queueSize: telemetry.queue_size,
      maxQueue: telemetry.max_queue_size,
      lastError: telemetry.last_error,
    };
  }, [telemetry, loading]);

  if (displayState.isLoading) {
    return (
      <div className="telemetry-panel">
        <h3>Telemetry (Real State Only)</h3>
        <div className="loading">{displayState.display}</div>
      </div>
    );
  }

  return (
    <div className="telemetry-panel">
      <h3>Telemetry (Real State Only)</h3>
      <div>
        <b>Serial Connected:</b>{' '}
        <span className={displayState.serialConnected ? 'ok' : 'error'}>
          {displayState.serialConnected ? 'Yes' : 'No'}
        </span>
      </div>
      <div>
        <b>Serial Port:</b> {displayState.serialPort || '-'}
      </div>
      <div>
        <b>Last Arduino Response:</b> {displayState.lastArduinoResponse || '-'}
      </div>
      <div>
        <b>Execution State:</b>{' '}
        <span className={`state-${displayState.executionState}`}>
          {displayState.executionState}
        </span>
      </div>
      <div>
        <b>Queue Size:</b> {displayState.queueSize} / {displayState.maxQueue}
      </div>
      <div>
        <b>Last Error:</b>{' '}
        <span className="error">{displayState.lastError || '-'}</span>
      </div>
    </div>
  );
}
