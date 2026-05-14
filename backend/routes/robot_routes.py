from flask import Blueprint, jsonify, request
from controllers.robot_controller import (
    handle_robot_command,
    handle_robot_stop,
    handle_robot_reset
)
from services.motion_engine import get_motion_status
from services.serial_service import get_serial_status

# ==========================================
# BLUEPRINT
# ==========================================

robot_routes = Blueprint("robot_routes", __name__)

# ==========================================
# MAIN ROBOT COMMAND ENDPOINT
# ==========================================

@robot_routes.route("/api/robot/command", methods=["POST"])
def robot_command():
    """
    Main robot motion control endpoint.
    
    Request JSON: {
        "servo1": 90,
        "servo2": 90,
        "servo3": 90,
        "servo4": 90,
        "servo5": 90,
        "servo6": 90
    }
    
    Response: {
        "success": bool,
        "state": str,
        "queue_size": int,
        "error": str or null
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        result = handle_robot_command(data)
        
        return jsonify({
            "success": result['success'],
            "state": result['state'],
            "queue_size": result['queue_size'],
            "error": result.get('error')
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# EMERGENCY STOP ENDPOINT
# ==========================================

@robot_routes.route("/api/robot/stop", methods=["POST"])
def robot_stop():
    """
    Emergency stop - clears motion queue.
    
    Response: {
        "success": bool,
        "state": str,
        "message": str
    }
    """
    try:
        result = handle_robot_stop()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# ROBOT RESET ENDPOINT
# ==========================================

@robot_routes.route("/api/robot/reset", methods=["POST"])
def robot_reset():
    """
    Reset motion engine to idle state.
    
    Response: {
        "success": bool,
        "message": str
    }
    """
    try:
        result = handle_robot_reset()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# STATUS ENDPOINTS
# ==========================================

@robot_routes.route("/api/robot/status", methods=["GET"])
def robot_status():
    """
    Returns current robot motion status.
    
    Response: {
        "motion": { state, queue_size, last_command, last_result, ... },
        "serial": { connected, port, baud_rate, ... }
    }
    """
    try:
        motion_status = get_motion_status()
        serial_status = get_serial_status()
        
        return jsonify({
            "motion": motion_status,
            "serial": serial_status
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# ==========================================
# TELEMETRY ENDPOINT (STUB FOR NOW)
# ==========================================

# ==========================================
# TELEMETRY ENDPOINT (REAL STATE ONLY)
# ==========================================

@robot_routes.route("/api/telemetry", methods=["GET"])
def telemetry():
    """
    Returns REAL robot telemetry data.
    Only exposes actual runtime state, no fake values.
    
    Fake telemetry (battery, temperature, speed) removed for engineering credibility.
    """
    try:
        motion_status = get_motion_status()
        serial_status = get_serial_status()
        
        return jsonify({
            "execution_state": motion_status['state'],
            "queue_size": motion_status['queue_size'],
            "max_queue_size": motion_status['max_queue_size'],
            "last_command": motion_status['last_command'],
            "last_error": motion_status['last_error'],
            "serial_connected": serial_status['connected'],
            "serial_port": serial_status['port'],
            "last_arduino_response": serial_status['last_response']
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500