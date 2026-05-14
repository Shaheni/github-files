from flask import Blueprint, jsonify, request
import logging
from services.speech_service import (
    get_voice_status,
    start_voice_recognition,
    stop_voice_recognition,
    get_voice_command,
    clear_voice_queue
)
from services.command_mapper import VOICE_COMMANDS

logger = logging.getLogger(__name__)

voice_bp = Blueprint('voice', __name__)

# ==========================================
# VOICE COMMAND ENDPOINTS
# ==========================================

@voice_bp.route('/api/voice/status')
def voice_status():
    """
    Get voice recognition status and command queue.
    
    Returns JSON:
    {
        "state": "idle|listening|processing|error|stopped",
        "running": bool,
        "queue_size": int,
        "command_count": int,
        "error_count": int,
        "last_command": string or null,
        "error": null or string,
        "supported_commands": [list of available commands]
    }
    """
    try:
        status = get_voice_status()
        status['supported_commands'] = list(VOICE_COMMANDS.keys())
        return jsonify(status), 200
    
    except Exception as e:
        logger.error(f"Voice status error: {e}")
        return jsonify({
            "error": str(e),
            "state": "unknown"
        }), 500

@voice_bp.route('/api/voice/start', methods=['POST'])
def voice_start():
    """
    Start voice recognition and command processing.
    
    Returns:
    {
        "success": bool,
        "message": string,
        "state": string
    }
    """
    try:
        status = get_voice_status()
        
        if status['running']:
            logger.warning("Voice already running")
            return jsonify({
                "success": False,
                "message": "Voice recognition already running",
                "state": status['state']
            }), 409
        
        success = start_voice_recognition()
        
        if success:
            logger.info("Voice recognition started")
            return jsonify({
                "success": True,
                "message": "Voice recognition started",
                "state": "listening"
            }), 200
        else:
            logger.error("Failed to start voice recognition")
            return jsonify({
                "success": False,
                "message": "Failed to start voice recognition"
            }), 500
    
    except Exception as e:
        logger.error(f"Voice start error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@voice_bp.route('/api/voice/stop', methods=['POST'])
def voice_stop():
    """
    Stop voice recognition.
    
    Returns:
    {
        "success": bool,
        "message": string
    }
    """
    try:
        success = stop_voice_recognition()
        
        if success:
            logger.info("Voice recognition stopped")
            return jsonify({
                "success": True,
                "message": "Voice recognition stopped"
            }), 200
        else:
            logger.warning("Voice was not running")
            return jsonify({
                "success": False,
                "message": "Voice recognition was not running"
            }), 409
    
    except Exception as e:
        logger.error(f"Voice stop error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@voice_bp.route('/api/voice/commands')
def voice_commands():
    """
    Get list of supported voice commands and their actions.
    
    Returns:
    {
        "commands": {
            "command_name": [servo_angles],
            ...
        },
        "total": int
    }
    """
    try:
        return jsonify({
            "commands": VOICE_COMMANDS,
            "total": len(VOICE_COMMANDS)
        }), 200
    
    except Exception as e:
        logger.error(f"Commands list error: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@voice_bp.route('/api/voice/command/next')
def get_next_command():
    """
    Get next recognized command from queue (removes from queue).
    
    Returns:
    {
        "command": {
            "text": string,
            "timestamp": float,
            "confidence": string
        }
    }
    or 204 if queue empty
    """
    try:
        cmd = get_voice_command()
        
        if cmd is None:
            return jsonify({
                "command": None,
                "queue_size": 0
            }), 204
        
        status = get_voice_status()
        return jsonify({
            "command": cmd,
            "queue_size": status['queue_size']
        }), 200
    
    except Exception as e:
        logger.error(f"Get command error: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@voice_bp.route('/api/voice/queue', methods=['GET', 'DELETE'])
def voice_queue():
    """
    GET: Get queue statistics (without removing commands)
    DELETE: Clear all pending commands
    
    GET Returns:
    {
        "queue_size": int,
        "queue_max": int
    }
    
    DELETE Returns:
    {
        "success": bool,
        "cleared": int (number of commands cleared)
    }
    """
    try:
        if request.method == 'GET':
            status = get_voice_status()
            return jsonify({
                "queue_size": status['queue_size'],
                "queue_max": status['queue_max']
            }), 200
        
        elif request.method == 'DELETE':
            cleared = clear_voice_queue()
            logger.info(f"Cleared {cleared} voice commands")
            return jsonify({
                "success": True,
                "cleared": cleared
            }), 200
    
    except Exception as e:
        logger.error(f"Queue operation error: {e}")
        return jsonify({
            "error": str(e)
        }), 500