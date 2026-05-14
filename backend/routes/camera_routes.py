from flask import Blueprint, Response, jsonify
import logging
from services.opencv_service import (
    generate_frames,
    get_camera_status,
    initialize_camera,
    shutdown_camera
)

logger = logging.getLogger(__name__)

camera_bp = Blueprint('camera', __name__)

# ==========================================
# CAMERA ENDPOINTS
# ==========================================

@camera_bp.route('/api/camera/video_feed')
def video_feed():
    """
    Stream live video feed as MJPEG.
    
    Returns: MJPEG stream with video/x-motion-jpeg mime type
    """
    try:
        status = get_camera_status()
        
        if status['state'] != 'running':
            return jsonify({
                "error": "Camera not running",
                "state": status['state']
            }), 503
        
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    
    except Exception as e:
        logger.error(f"Video feed error: {e}")
        return jsonify({
            "error": f"Video feed error: {str(e)}"
        }), 500

@camera_bp.route('/api/camera/status')
def camera_status():
    """
    Get camera status and statistics.
    
    Returns JSON:
    {
        "state": "idle|initializing|running|error|stopped",
        "running": bool,
        "frame_count": int,
        "frames_buffered": int,
        "error": null or string,
        "resolution": "WxH",
        "fps": int
    }
    """
    try:
        status = get_camera_status()
        return jsonify(status), 200
    
    except Exception as e:
        logger.error(f"Status request error: {e}")
        return jsonify({
            "error": str(e),
            "state": "unknown"
        }), 500

@camera_bp.route('/api/camera/start', methods=['POST'])
def camera_start():
    """
    Start camera and begin video capture.
    
    Returns:
    {
        "success": bool,
        "message": string,
        "state": string
    }
    """
    try:
        status = get_camera_status()
        
        if status['state'] in ['running', 'initializing']:
            logger.warning("Camera already running or initializing")
            return jsonify({
                "success": False,
                "message": f"Camera already {status['state']}",
                "state": status['state']
            }), 409
        
        success = initialize_camera()
        
        if success:
            logger.info("Camera started successfully")
            return jsonify({
                "success": True,
                "message": "Camera started",
                "state": "initializing"
            }), 200
        else:
            logger.error("Failed to start camera")
            return jsonify({
                "success": False,
                "message": "Failed to start camera",
                "state": status['state']
            }), 500
    
    except Exception as e:
        logger.error(f"Camera start error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@camera_bp.route('/api/camera/stop', methods=['POST'])
def camera_stop():
    """
    Stop camera and release resources.
    
    Returns:
    {
        "success": bool,
        "message": string
    }
    """
    try:
        success = shutdown_camera()
        
        if success:
            logger.info("Camera stopped successfully")
            return jsonify({
                "success": True,
                "message": "Camera stopped"
            }), 200
        else:
            logger.warning("Camera was not running")
            return jsonify({
                "success": False,
                "message": "Camera was not running"
            }), 409
    
    except Exception as e:
        logger.error(f"Camera stop error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500