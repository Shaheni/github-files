/**
 * CameraPanel - Live camera feed and controls
 * Displays MJPEG video stream with status and control buttons
 */

import React, { useState, useCallback } from 'react';
import { startCamera, stopCamera, getCameraStatus } from '../api/robotApi';
import { logger } from '../utils/logger';

/**
 * CameraPanel Component
 * @param {Object} cameraStatus - Current camera status from backend
 * @param {Function} onStatusUpdate - Callback when status changes
 */
export default function CameraPanel({ cameraStatus, onStatusUpdate }) {
  const [sendingCommand, setSendingCommand] = useState(false);
  const [error, setError] = useState(null);

  const isRunning = cameraStatus?.state === 'running';

  /**
   * Start camera capture
   */
  const handleStartCamera = useCallback(async () => {
    setSendingCommand(true);
    setError(null);

    try {
      logger.info('User clicked: Start Camera');
      const result = await startCamera();

      if (result.type === 'success') {
        logger.info('Camera started successfully');
        // Fetch updated status
        setTimeout(() => {
          onStatusUpdate?.();
        }, 500);
      } else {
        logger.error('Failed to start camera', result.error);
        setError(result.error || 'Failed to start camera');
      }
    } catch (err) {
      logger.error('Start camera error', { error: err.message });
      setError('Error starting camera');
    } finally {
      setSendingCommand(false);
    }
  }, [onStatusUpdate]);

  /**
   * Stop camera capture
   */
  const handleStopCamera = useCallback(async () => {
    setSendingCommand(true);
    setError(null);

    try {
      logger.info('User clicked: Stop Camera');
      const result = await stopCamera();

      if (result.type === 'success') {
        logger.info('Camera stopped successfully');
        // Fetch updated status
        setTimeout(() => {
          onStatusUpdate?.();
        }, 500);
      } else {
        logger.error('Failed to stop camera', result.error);
        setError(result.error || 'Failed to stop camera');
      }
    } catch (err) {
      logger.error('Stop camera error', { error: err.message });
      setError('Error stopping camera');
    } finally {
      setSendingCommand(false);
    }
  }, [onStatusUpdate]);

  return (
    <div className="camera-panel panel">
      <h2>Live Camera Feed</h2>

      <div className="camera-status">
        <div className="status-badge">
          <span className={`indicator ${isRunning ? 'running' : 'stopped'}`}></span>
          {isRunning ? 'Running' : 'Stopped'}
        </div>
        {cameraStatus?.frame_count !== undefined && (
          <div className="stats">
            <span>Frames: {cameraStatus.frame_count}</span>
            <span>Buffer: {cameraStatus.frames_buffered}/2</span>
          </div>
        )}
      </div>

      <div className="video-container">
        {isRunning ? (
          <img
            src={`${window.location.protocol}//${window.location.hostname}:5050/api/camera/video_feed`}
            alt="Robot Camera Feed"
            className="video-feed"
            onError={(e) => {
              logger.error('Video feed load error');
              setError('Failed to load video stream');
            }}
          />
        ) : (
          <div className="video-placeholder">
            <div className="placeholder-content">
              <p>Camera not running</p>
              <p style={{ fontSize: '12px', marginTop: '10px' }}>Click Start to begin streaming</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message" role="alert">
          ⚠️ {error}
        </div>
      )}

      <div className="button-group">
        <button
          onClick={handleStartCamera}
          disabled={isRunning || sendingCommand}
          className="btn btn-primary"
          aria-label="Start camera"
        >
          {sendingCommand ? 'Starting...' : 'Start Camera'}
        </button>

        <button
          onClick={handleStopCamera}
          disabled={!isRunning || sendingCommand}
          className="btn btn-secondary"
          aria-label="Stop camera"
        >
          {sendingCommand ? 'Stopping...' : 'Stop Camera'}
        </button>
      </div>

      {cameraStatus?.error && (
        <div className="hardware-error" role="alert">
          Hardware Error: {cameraStatus.error}
        </div>
      )}
    </div>
  );
}
