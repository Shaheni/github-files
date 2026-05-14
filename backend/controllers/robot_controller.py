import logging
from services.motion_engine import execute_motion_command, stop_motion, reset_motion_engine

logger = logging.getLogger(__name__)

# ==========================================
# ROBOT MOTION CONTROL
# ==========================================

def handle_robot_command(request_data):
    """
    Handles a robot motion command from frontend.
    
    Routes through motion_engine which manages queue and execution.
    
    Args:
        request_data (dict): JSON with servo1-servo6 values
    
    Returns:
        dict: Result from motion engine
    """
    logger.info(f"Robot command handler: {request_data}")
    return execute_motion_command(request_data)

# ==========================================
# ROBOT STOP COMMAND
# ==========================================

def handle_robot_stop():
    """
    Handles emergency stop.
    Clears queue and stops current motion.
    
    Returns:
        dict: Result of stop operation
    """
    logger.info("Robot stop command")
    return stop_motion()

# ==========================================
# ROBOT RESET
# ==========================================

def handle_robot_reset():
    """
    Handles robot reset.
    Resets motion engine to initial state.
    
    Returns:
        dict: Result of reset operation
    """
    logger.info("Robot reset command")
    return reset_motion_engine()