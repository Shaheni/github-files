import logging

logger = logging.getLogger(__name__)

# ==========================================
# SERVO CONFIGURATION (FROM ARDUINO)
# ==========================================

TOTAL_SERVOS = 6

# Minimum angle for each servo (from Arduino servoMin array)
SERVO_MIN = [0, 10, 10, 0, 0, 0]

# Maximum angle for each servo (from Arduino servoMax array)
SERVO_MAX = [180, 170, 170, 180, 180, 180]

# ==========================================
# VALIDATE SERVO VALUES
# ==========================================

def validate_servo_values(angles_dict):
    """
    Validates servo values from frontend request.
    
    Args:
        angles_dict (dict): Dictionary with servo1-servo6 keys
    
    Returns:
        tuple: (is_valid, angles_list or error_message)
    """
    
    # Extract servo values
    servo_values = []
    
    for i in range(1, TOTAL_SERVOS + 1):
        key = f"servo{i}"
        
        if key not in angles_dict:
            return False, f"Missing {key}"
        
        try:
            value = int(angles_dict[key])
        except (ValueError, TypeError):
            return False, f"{key} must be an integer"
        
        # Check bounds for this servo
        if value < SERVO_MIN[i - 1] or value > SERVO_MAX[i - 1]:
            return False, f"{key} out of bounds: {value} (valid: {SERVO_MIN[i-1]}-{SERVO_MAX[i-1]})"
        
        servo_values.append(value)
    
    return True, servo_values

# ==========================================
# BUILD ARDUINO PACKET
# ==========================================

def build_packet(angles_list):
    """
    Builds exact Arduino packet format.
    
    Args:
        angles_list (list): List of 6 servo angles
    
    Returns:
        str: Packet in format "val1,val2,val3,val4,val5,val6\n"
    """
    
    if len(angles_list) != TOTAL_SERVOS:
        raise ValueError(f"Expected {TOTAL_SERVOS} angles, got {len(angles_list)}")
    
    packet = ",".join(map(str, angles_list)) + "\n"
    return packet

# ==========================================
# PROCESS ROBOT COMMAND (MAIN ENTRY POINT)
# ==========================================

def process_robot_command(request_data):
    """
    Validates and processes a robot command from frontend.
    
    Args:
        request_data (dict): JSON data from frontend
    
    Returns:
        dict: {
            'success': bool,
            'packet': str or None,
            'angles': list or None,
            'error': str or None
        }
    """
    
    logger.info(f"Processing robot command: {request_data}")
    
    # Validate servo values
    is_valid, result = validate_servo_values(request_data)
    
    if not is_valid:
        logger.warning(f"Validation failed: {result}")
        return {
            'success': False,
            'packet': None,
            'angles': None,
            'error': result
        }
    
    # Build packet
    angles_list = result
    try:
        packet = build_packet(angles_list)
        logger.info(f"Built packet: {packet.strip()}")
        return {
            'success': True,
            'packet': packet,
            'angles': angles_list,
            'error': None
        }
    except Exception as e:
        logger.error(f"Packet building failed: {str(e)}")
        return {
            'success': False,
            'packet': None,
            'angles': None,
            'error': str(e)
        }