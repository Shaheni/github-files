from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

from routes.robot_routes import robot_routes
from routes.camera_routes import camera_bp
from routes.voice_routes import voice_bp
from services.serial_service import initialize_serial
from services.opencv_service import shutdown_camera
from services.speech_service import stop_voice_recognition

import os
import logging

# ==========================================
# LOGGING SETUP
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# FRONTEND PATH
# ==========================================

frontend_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend"
)

# ==========================================
# FLASK APP INITIALIZATION
# ==========================================

app = Flask(
    __name__,
    static_folder=frontend_path,
    static_url_path=""
)

CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

# ==========================================
# REGISTER BLUEPRINTS
# ==========================================

app.register_blueprint(robot_routes)
app.register_blueprint(camera_bp)
app.register_blueprint(voice_bp)

# ==========================================
# INITIALIZE ARDUINO CONNECTION ON STARTUP
# ==========================================

@app.before_request
def startup():
    """Initialize serial connection before first request."""
    if not hasattr(app, 'arduino_initialized'):
        logger.info("Initializing Arduino connection...")
        initialize_serial()
        app.arduino_initialized = True

# ==========================================
# SERVE FRONTEND
# ==========================================

@app.route("/")
def serve_frontend():
    """Serve main frontend index.html"""
    return send_from_directory(frontend_path, "index.html")

# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Real health check - verifies:
    * Serial port is open
    * Arduino has responded with valid message
    
    Returns true only if backend can communicate with Arduino.
    """
    from services.serial_service import is_serial_connected, get_serial_status
    
    serial_status = get_serial_status()
    is_connected = is_serial_connected()
    has_arduino_response = serial_status['last_response'] in ['OK', 'ROBOT_READY', 'INVALID_PACKET']
    
    arduino_healthy = is_connected and has_arduino_response
    
    return {
        "status": "ok",
        "backend_ready": True,
        "serial_connected": is_connected,
        "arduino_responsive": arduino_healthy,
        "last_arduino_response": serial_status['last_response']
    }

# ==========================================
# GRACEFUL SHUTDOWN
# ==========================================

@app.teardown_appcontext
def cleanup(error):
    """
    Cleanup resources on app shutdown.
    """
    logger.info("Cleaning up resources...")
    
    try:
        shutdown_camera()
        logger.info("Camera shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down camera: {e}")
    
    try:
        stop_voice_recognition()
        logger.info("Voice recognition shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down voice: {e}")

# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":
    logger.info("Starting Flask server on 127.0.0.1:5050")
    try:
        socketio.run(
            app,
            host="127.0.0.1",
            port=5050,
            debug=True
        )
    finally:
        logger.info("Server shutdown")
        shutdown_camera()
        stop_voice_recognition()