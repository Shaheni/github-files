/**
 * ConnectionStatus - Display robot connection status
 * Shows backend and Arduino connectivity
 */

import React, { useMemo } from 'react';

/**
 * ConnectionStatus Component
 * @param {Object} health - health check response
 * @param {boolean} backendOffline - backend unavailable flag
 */
export default function ConnectionStatus({ health, backendOffline }) {
  const statusInfo = useMemo(() => {
    if (backendOffline) {
      return { status: 'Backend Offline', class: 'error' };
    }
    if (!health) {
      return { status: 'Checking...', class: 'loading' };
    }
    if (health.arduino_responsive && health.serial_connected) {
      return { status: 'Connected & Ready', class: 'ok' };
    }
    if (health.serial_connected) {
      return { status: 'Serial Only (Arduino Not Responding)', class: 'warning' };
    }
    return { status: 'Not Connected', class: 'error' };
  }, [health, backendOffline]);

  return (
    <div
      className={`connection-status ${statusInfo.class}`}
      role="status"
      aria-live="polite"
    >
      <b>Status:</b> {statusInfo.status}
    </div>
  );
}
