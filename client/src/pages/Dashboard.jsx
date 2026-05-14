/**
 * Dashboard - Main robot control interface
 * Production-grade dashboard with health monitoring and state management
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  getRobotStatus,
  getTelemetry,
  healthCheck,
  getCameraStatus,
  getVoiceStatus,
} from '../api/robotApi';
import { POLLING_INTERVAL_MS } from '../constants/servoConfig';
import { logger } from '../utils/logger';
import ServoControls from '../components/ServoControls';
import StatusPanel from '../components/StatusPanel';
import TelemetryPanel from '../components/TelemetryPanel';
import ConnectionStatus from '../components/ConnectionStatus';
import EmergencyControls from '../components/EmergencyControls';
import CameraPanel from '../components/CameraPanel';
import VoicePanel from '../components/VoicePanel';

/**
 * Dashboard Component
 * Main interface for robot control and monitoring
 */
export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [health, setHealth] = useState(null);
  const [cameraStatus, setCameraStatus] = useState(null);
  const [voiceStatus, setVoiceStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendOffline, setBackendOffline] = useState(false);
  const [lastPollTime, setLastPollTime] = useState(null);
  const [pollErrors, setPollErrors] = useState(0);

  /**
   * Fetch all backend data
   */
  const fetchAll = useCallback(async () => {
    try {
      const [statusRes, telemetryRes, healthRes, cameraRes, voiceRes] = await Promise.all([
        getRobotStatus(),
        getTelemetry(),
        healthCheck(),
        getCameraStatus(),
        getVoiceStatus(),
      ]);

      // Check if any request indicates backend offline
      const isOffline =
        statusRes.type === 'backend_offline' ||
        telemetryRes.type === 'backend_offline' ||
        healthRes.type === 'backend_offline';

      if (isOffline) {
        logger.warn('Backend offline detected');
        setBackendOffline(true);
      } else {
        setBackendOffline(false);
        setStatus(statusRes);
        setTelemetry(telemetryRes);
        setHealth(healthRes);
        setCameraStatus(cameraRes);
        setVoiceStatus(voiceRes);
        setPollErrors(0); // Reset error count on success
      }

      setLastPollTime(new Date());
      setLoading(false);
    } catch (err) {
      logger.error('Dashboard fetch failed', { error: err.message });
      setPollErrors(prev => prev + 1);
    }
  }, []);

  /**
   * Initial mount - fetch immediately then start polling
   */
  useEffect(() => {
    logger.info('Dashboard mounted, initiating immediate fetch');
    fetchAll();

    const interval = setInterval(fetchAll, POLLING_INTERVAL_MS);

    return () => {
      clearInterval(interval);
      logger.info('Dashboard cleanup - polling interval cleared');
    };
  }, [fetchAll]);

  /**
   * Log polling performance in development
   */
  useEffect(() => {
    if (import.meta.env.DEV && pollErrors > 0) {
      logger.debug('Polling error count', { errors: pollErrors });
    }
  }, [pollErrors]);

  return (
    <div className="dashboard">
      <h1>Robot Arm Control Panel</h1>

      <ConnectionStatus health={health} backendOffline={backendOffline} />

      {backendOffline && (
        <div className="backend-offline-message" role="alert">
          ⚠️ Backend server is offline. Cannot connect to robot control system.
        </div>
      )}

      {pollErrors > 2 && (
        <div className="polling-error-notice" role="alert">
          ⚠️ Multiple connection issues detected. Please check backend server.
        </div>
      )}

      <div className="control-section">
        <ServoControls
          disabled={!health?.arduino_responsive}
          backendOffline={backendOffline}
          onCommandSent={fetchAll}
        />

        <EmergencyControls
          onStop={fetchAll}
          onReset={fetchAll}
        />
      </div>

      <div className="status-section">
        <StatusPanel motion={status?.motion} loading={loading} />
        <TelemetryPanel telemetry={telemetry} loading={loading} />
      </div>

      <div className="camera-voice-section">
        <CameraPanel
          cameraStatus={cameraStatus}
          onStatusUpdate={fetchAll}
        />

        <VoicePanel
          voiceStatus={voiceStatus}
          onStatusUpdate={fetchAll}
          onCommandReceived={(cmd) => {
            logger.info('Voice command to be processed', cmd);
          }}
        />
      </div>

      {lastPollTime && import.meta.env.DEV && (
        <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
          Last poll: {lastPollTime.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
