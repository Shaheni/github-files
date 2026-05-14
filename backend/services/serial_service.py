import serial
import time
import logging

# ==========================================
# SERIAL CONFIGURATION
# ==========================================

SERIAL_PORT = "COM5"
BAUD_RATE = 115200
RESPONSE_TIMEOUT = 0.5  # seconds
MAX_RETRIES = 2

# ==========================================
# LOGGING SETUP
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# GLOBAL SERIAL CONNECTION STATE
# ==========================================

arduino = None
is_connected = False
last_response = ""

# ==========================================
# INITIALIZE SERIAL CONNECTION
# ==========================================

def initialize_serial():
    """
    Opens serial connection to Arduino.
    Returns True if successful, False otherwise.
    """
    global arduino, is_connected, last_response
    
    try:
        if arduino is None or not arduino.is_open:
            arduino = serial.Serial(
                SERIAL_PORT,
                BAUD_RATE,
                timeout=RESPONSE_TIMEOUT
            )
            time.sleep(2)  # Wait for Arduino to be ready
            
            # Read startup message from Arduino
            if arduino.in_waiting:
                startup_msg = arduino.readline().decode().strip()
                logger.info(f"Arduino startup: {startup_msg}")
                last_response = startup_msg
            
            is_connected = True
            logger.info("Serial connection established")
            return True
        else:
            is_connected = True
            return True
            
    except Exception as e:
        is_connected = False
        logger.error(f"Failed to initialize serial: {str(e)}")
        return False

# ==========================================
# CHECK CONNECTION STATUS
# ==========================================

def is_serial_connected():
    """Returns True if Arduino is connected, False otherwise."""
    global arduino, is_connected
    
    if arduino is None or not arduino.is_open:
        is_connected = False
        return False
    
    is_connected = True
    return True

# ==========================================
# SEND COMMAND AND WAIT FOR RESPONSE
# ==========================================

def send_command_to_arduino(packet, retries=1):
    """
    Sends a packet to Arduino and waits for response.
    
    IMPORTANT: NO automatic retries for demo predictability.
    Sends ONCE. On timeout or error, returns failure.
    Operator must manually retry if needed.
    
    Args:
        packet (str): Command packet ending with \n
        retries (int): UNUSED - always sends once only for demo
    
    Returns:
        dict: {
            'success': bool,
            'response': str (OK/INVALID_PACKET/TIMEOUT/ERROR),
            'error': str or None
        }
    """
    global arduino, is_connected, last_response
    
    # Ensure serial is initialized
    if not is_serial_connected():
        if not initialize_serial():
            logger.error("Cannot send command: Serial not connected")
            return {
                'success': False,
                'response': 'DISCONNECTED',
                'error': 'Arduino not connected'
            }
    
    try:
        # Clear input buffer to avoid stale data
        arduino.reset_input_buffer()
        
        # Send packet ONCE
        logger.info(f"Sending command: {packet.strip()}")
        arduino.write(packet.encode())
        arduino.flush()
        
        # Wait for response with timeout
        response = arduino.readline().decode().strip()
        
        if response:
            last_response = response
            logger.info(f"Arduino response: {response}")
            
            if response == "OK":
                return {
                    'success': True,
                    'response': 'OK',
                    'error': None
                }
            elif response == "INVALID_PACKET":
                logger.warning(f"Invalid packet rejected by Arduino")
                return {
                    'success': False,
                    'response': 'INVALID_PACKET',
                    'error': 'Arduino rejected packet format'
                }
            else:
                # Unexpected response
                logger.warning(f"Unexpected response: {response}")
                return {
                    'success': False,
                    'response': response,
                    'error': f'Unexpected response: {response}'
                }
        else:
            # Timeout reading response
            logger.error(f"Timeout: No response from Arduino")
            last_response = "TIMEOUT"
            return {
                'success': False,
                'response': 'TIMEOUT',
                'error': 'No response from Arduino - check serial connection'
            }
    
    except Exception as e:
        logger.error(f"Serial communication error: {str(e)}")
        is_connected = False
        last_response = "ERROR"
        return {
            'success': False,
            'response': 'ERROR',
            'error': str(e)
        }

# ==========================================
# GET CONNECTION STATUS
# ==========================================

def get_serial_status():
    """Returns current serial connection status."""
    return {
        'connected': is_serial_connected(),
        'port': SERIAL_PORT,
        'baud_rate': BAUD_RATE,
        'last_response': last_response
    }