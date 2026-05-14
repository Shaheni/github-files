import logging
from services.speech_service import (
    voice_manager,
    start_voice_recognition,
    stop_voice_recognition,
    get_voice_status,
    get_voice_command
)
from services.command_mapper import VOICE_COMMANDS
from services.motion_engine import execute_motion_command

logger = logging.getLogger(__name__)

# ==========================================
# VOICE COMMAND CONTROLLER
# ==========================================

def start_voice():
    """
    Start voice command recognition.
    """
    logger.info("Starting voice recognition...")
    success = start_voice_recognition()
    if success:
        logger.info("Voice recognition started")
    else:
        logger.error("Failed to start voice recognition")
    return success

def stop_voice():
    """
    Stop voice command recognition.
    """
    logger.info("Stopping voice recognition...")
    success = stop_voice_recognition()
    if success:
        logger.info("Voice recognition stopped")
    else:
        logger.warning("Voice was not running")
    return success

def process_voice_commands():
    """
    Process one pending voice command from queue.
    
    Returns:
    {
        "success": bool,
        "command": str or None,
        "action": dict or None,
        "message": str
    }
    """
    # Get next command from queue
    cmd_data = get_voice_command()
    
    if not cmd_data:
        return {
            "success": False,
            "command": None,
            "action": None,
            "message": "No pending commands"
        }
    
    text = cmd_data['text']
    logger.info(f"Processing voice command: '{text}'")
    
    # Check if command is in our mapping
    if text not in VOICE_COMMANDS:
        logger.warning(f"Unknown command: '{text}'")
        return {
            "success": False,
            "command": text,
            "action": None,
            "message": f"Unknown command: '{text}'"
        }
    
    # Get servo angles for this command
    angles = VOICE_COMMANDS[text]
    
    # Build command dict for motion engine
    command_dict = {
        f"servo{i+1}": angles[i]
        for i in range(6)
    }
    
    logger.info(f"Executing motion: {text} -> {angles}")
    
    # Send to motion engine
    result = execute_motion_command(command_dict)
    
    if result['success']:
        logger.info(f"✅ Voice command executed: {text}")
        return {
            "success": True,
            "command": text,
            "action": angles,
            "message": f"Executed: {text}"
        }
    else:
        logger.error(f"❌ Failed to execute: {result.get('error')}")
        return {
            "success": False,
            "command": text,
            "action": None,
            "message": result.get('error', 'Unknown error')
        }

def get_voice_status_dict():
    """
    Get voice recognition status.
    """
    return get_voice_status()