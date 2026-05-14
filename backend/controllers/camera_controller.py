import logging
from services.opencv_service import (
    camera_manager,
    get_camera_status,
    initialize_camera,
    shutdown_camera
)

logger = logging.getLogger(__name__)

# ==========================================
# CAMERA CONTROLLER
# ==========================================

def start_camera():
    """
    Start camera for video streaming.
    """
    logger.info("Starting camera...")
    success = initialize_camera()
    if success:
        logger.info("Camera started successfully")
    else:
        logger.error("Failed to start camera")
    return success

def stop_camera():
    """
    Stop camera and release resources.
    """
    logger.info("Stopping camera...")
    success = shutdown_camera()
    if success:
        logger.info("Camera stopped successfully")
    else:
        logger.warning("Camera was not running")
    return success

def get_camera_status_dict():
    """
    Get current camera status.
    """
    return get_camera_status()