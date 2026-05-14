/**
 * VoicePanel - Voice command recognition and status
 * Displays voice status, recognized commands, and controls
 */

import React, { useState, useCallback } from 'react';
import { startVoice, stopVoice, getVoiceCommand } from '../api/robotApi';
import { logger } from '../utils/logger';

/**
 * VoicePanel Component
 * @param {Object} voiceStatus - Current voice status from backend
 * @param {Function} onStatusUpdate - Callback when status changes
 * @param {Function} onCommandReceived - Callback when new command is received
 */
export default function VoicePanel({ voiceStatus, onStatusUpdate, onCommandReceived }) {
  const [sendingCommand, setSendingCommand] = useState(false);
  const [error, setError] = useState(null);
  const [recentCommands, setRecentCommands] = useState([]);

  const isRunning = voiceStatus?.running === true;
  const state = voiceStatus?.state || 'unknown';
  const queueSize = voiceStatus?.queue_size || 0;
  const commandCount = voiceStatus?.command_count || 0;
  const errorCount = voiceStatus?.error_count || 0;

  /**
   * Start voice recognition
   */
  const handleStartVoice = useCallback(async () => {
    setSendingCommand(true);
    setError(null);

    try {
      logger.info('User clicked: Start Voice');
      const result = await startVoice();

      if (result.type === 'success') {
        logger.info('Voice recognition started');
        // Fetch updated status
        setTimeout(() => {
          onStatusUpdate?.();
        }, 500);
      } else {
        logger.error('Failed to start voice', result.error);
        setError(result.error || 'Failed to start voice');
      }
    } catch (err) {
      logger.error('Start voice error', { error: err.message });
      setError('Error starting voice');
    } finally {
      setSendingCommand(false);
    }
  }, [onStatusUpdate]);

  /**
   * Stop voice recognition
   */
  const handleStopVoice = useCallback(async () => {
    setSendingCommand(true);
    setError(null);

    try {
      logger.info('User clicked: Stop Voice');
      const result = await stopVoice();

      if (result.type === 'success') {
        logger.info('Voice recognition stopped');
        // Fetch updated status
        setTimeout(() => {
          onStatusUpdate?.();
        }, 500);
      } else {
        logger.error('Failed to stop voice', result.error);
        setError(result.error || 'Failed to stop voice');
      }
    } catch (err) {
      logger.error('Stop voice error', { error: err.message });
      setError('Error stopping voice');
    } finally {
      setSendingCommand(false);
    }
  }, [onStatusUpdate]);

  /**
   * Get next command from queue
   */
  const handleGetCommand = useCallback(async () => {
    try {
      logger.debug('Fetching next voice command...');
      const result = await getVoiceCommand();

      if (result.type === 'success' && result.command) {
        const command = result.command.text;
        logger.info('Voice command received', { command });
        
        // Add to recent commands list
        setRecentCommands(prev => [
          { text: command, timestamp: new Date().getTime() },
          ...prev.slice(0, 4)
        ]);

        // Call callback
        onCommandReceived?.({ command, timestamp: result.command.timestamp });
      }
    } catch (err) {
      logger.error('Get command error', { error: err.message });
    }
  }, [onCommandReceived]);

  /**
   * Get state indicator color
   */
  const getStateColor = () => {
    switch (state) {
      case 'listening':
        return 'listening';
      case 'processing':
        return 'processing';
      case 'error':
        return 'error';
      case 'idle':
        return isRunning ? 'idle' : 'stopped';
      default:
        return 'unknown';
    }
  };

  return (
    <div className="voice-panel panel">
      <h2>Voice Command Recognition</h2>

      <div className="voice-status">
        <div className="status-badge">
          <span className={`indicator ${getStateColor()}`}></span>
          <span className="state-text">
            {isRunning ? `Listening (${state})` : 'Not Active'}
          </span>
        </div>

        <div className="voice-stats">
          <div className="stat-item">
            <span className="stat-label">Queue:</span>
            <span className="stat-value">{queueSize}/10</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Recognized:</span>
            <span className="stat-value">{commandCount}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Errors:</span>
            <span className={`stat-value ${errorCount > 0 ? 'error' : ''}`}>
              {errorCount}
            </span>
          </div>
        </div>
      </div>

      {voiceStatus?.last_command && (
        <div className="last-command">
          <span className="label">Last Recognized:</span>
          <span className="command-text">"{voiceStatus.last_command}"</span>
        </div>
      )}

      {recentCommands.length > 0 && (
        <div className="recent-commands">
          <h3>Recent Commands</h3>
          <ul>
            {recentCommands.map((cmd, idx) => (
              <li key={idx} className="command-item">
                <span className="command-text">"{cmd.text}"</span>
                <span className="command-time">
                  {new Date(cmd.timestamp).toLocaleTimeString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div className="error-message" role="alert">
          ⚠️ {error}
        </div>
      )}

      {voiceStatus?.error && (
        <div className="hardware-error" role="alert">
          Error: {voiceStatus.error}
        </div>
      )}

      <div className="button-group">
        <button
          onClick={handleStartVoice}
          disabled={isRunning || sendingCommand}
          className="btn btn-primary"
          aria-label="Start voice recognition"
        >
          {sendingCommand ? 'Starting...' : '🎤 Start Listening'}
        </button>

        <button
          onClick={handleStopVoice}
          disabled={!isRunning || sendingCommand}
          className="btn btn-secondary"
          aria-label="Stop voice recognition"
        >
          {sendingCommand ? 'Stopping...' : '⏹️ Stop Listening'}
        </button>

        <button
          onClick={handleGetCommand}
          disabled={queueSize === 0}
          className="btn btn-info"
          aria-label="Get next command"
        >
          📥 Get Command ({queueSize})
        </button>
      </div>

      <div className="voice-info">
        <p>
          📢 {isRunning
            ? 'Listening for voice commands. Speak clearly for best recognition.'
            : 'Click Start Listening to begin voice command recognition.'}
        </p>
      </div>
    </div>
  );
}
