import logging
from collections import deque
from services.serial_service import send_command_to_arduino
from services.command_mapper import process_robot_command

logger = logging.getLogger(__name__)

# ==========================================
# EXECUTION STATE ENUM
# ==========================================

class ExecutionState:
    IDLE = "idle"
    EXECUTING = "executing"
    ERROR = "error"
    STOPPED = "stopped"

# ==========================================
# QUEUE CONFIGURATION
# ==========================================

MAX_QUEUE_SIZE = 3  # Limit queue to prevent frontend spam

# ==========================================
# GLOBAL MOTION ENGINE STATE
# ==========================================

command_queue = deque()
current_state = ExecutionState.IDLE
last_command = None
last_result = None
last_error = None

# ==========================================
# EXECUTE MOTION COMMAND
# ==========================================

def execute_motion_command(request_data):
    """
    Main entry point for executing a motion command.
    
    Commands are queued and executed one at a time.
    NO automatic retries - single send only.
    If timeout or error, manual retry required.
    
    Args:
        request_data (dict): Frontend request with servo1-servo6
    
    Returns:
        dict: {
            'success': bool,
            'state': str,
            'queue_size': int,
            'result': dict or None,
            'error': str or None
        }
    """
    global current_state, command_queue, last_error
    
    logger.info(f"Motion command received: {request_data}")
    
    # Check queue size
    if len(command_queue) >= MAX_QUEUE_SIZE:
        logger.warning(f"Queue full: {len(command_queue)}/{MAX_QUEUE_SIZE}")
        last_error = f"Queue full: {len(command_queue)} commands pending"
        return {
            'success': False,
            'state': current_state,
            'queue_size': len(command_queue),
            'result': None,
            'error': last_error
        }
    
    # Validate and map command
    map_result = process_robot_command(request_data)
    
    if not map_result['success']:
        logger.warning(f"Command validation failed: {map_result['error']}")
        last_error = map_result['error']
        return {
            'success': False,
            'state': current_state,
            'queue_size': len(command_queue),
            'result': None,
            'error': map_result['error']
        }
    
    # Add to queue
    command_queue.append({
        'packet': map_result['packet'],
        'angles': map_result['angles'],
        'validation_result': map_result
    })
    
    logger.info(f"Command queued. Queue size: {len(command_queue)}/{MAX_QUEUE_SIZE}")
    
    # If idle, start executing immediately
    if current_state == ExecutionState.IDLE:
        _process_queue()
    
    return {
        'success': True,
        'state': current_state,
        'queue_size': len(command_queue),
        'result': None,
        'error': None
    }

# ==========================================
# PROCESS COMMAND QUEUE
# ==========================================

def _process_queue():
    """
    Processes the next command in the queue.
    Runs synchronously - waits for Arduino response before processing next.
    
    IMPORTANT: NO automatic retries.
    Send once only. On timeout/error, require manual retry.
    """
    global current_state, command_queue, last_command, last_result, last_error
    
    # If queue empty, go back to idle
    if not command_queue:
        current_state = ExecutionState.IDLE
        logger.info("Queue empty, returning to idle state")
        return
    
    # Get next command
    current_state = ExecutionState.EXECUTING
    cmd = command_queue.popleft()
    last_command = cmd
    
    logger.info(f"Executing command: {cmd['packet'].strip()}")
    
    # Send to Arduino - ONCE ONLY
    result = send_command_to_arduino(cmd['packet'], retries=1)
    last_result = result
    
    if result['success']:
        logger.info(f"Command executed successfully")
        last_error = None
        
        # Process next command if any
        if command_queue:
            _process_queue()
        else:
            current_state = ExecutionState.IDLE
    else:
        # Command failed - enter error state
        logger.error(f"Command failed: {result['error']}")
        last_error = result['error']
        current_state = ExecutionState.ERROR
        # Do NOT retry, do NOT clear queue - let operator manually retry

# ==========================================
# GET MOTION ENGINE STATUS
# ==========================================

def get_motion_status():
    """Returns current motion engine state."""
    return {
        'state': current_state,
        'queue_size': len(command_queue),
        'max_queue_size': MAX_QUEUE_SIZE,
        'last_command': last_command['packet'].strip() if last_command else None,
        'last_result': last_result,
        'last_error': last_error
    }

# ==========================================
# STOP MOTION (CLEAR QUEUE)
# ==========================================

def stop_motion():
    """Clears queue and stops current command."""
    global current_state, command_queue, last_error
    
    logger.info("Motion stopped by operator")
    current_state = ExecutionState.STOPPED
    command_queue.clear()
    last_error = "Motion stopped by operator"
    
    return {
        'success': True,
        'state': current_state,
        'message': 'Motion queue cleared'
    }

# ==========================================
# RESET MOTION ENGINE
# ==========================================

def reset_motion_engine():
    """Resets motion engine to initial state."""
    global current_state, command_queue, last_command, last_result, last_error
    
    logger.info("Motion engine reset")
    current_state = ExecutionState.IDLE
    command_queue.clear()
    last_command = None
    last_result = None
    last_error = None
    
    return {
        'success': True,
        'message': 'Motion engine reset to idle'
    }