import time
import logging

# ==========================================
# MOCK SERIAL SERVICE FOR TESTING WITHOUT HARDWARE
# ==========================================

SERIAL_PORT = "MOCK"
BAUD_RATE = 115200
RESPONSE_TIMEOUT = 0.5  # seconds
MAX_RETRIES = 2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock state
is_connected = True
last_response = "MOCK_OK"

# ==========================================
# MOCK INITIALIZE SERIAL
# ==========================================
def initialize_serial():
    global is_connected, last_response
    is_connected = True
    last_response = "MOCK_ROBOT_READY"
    logger.info("[MOCK] Serial connection initialized (no hardware)")
    return True

# ==========================================
# MOCK CHECK CONNECTION
# ==========================================
def is_serial_connected():
    global is_connected
    return is_connected

# ==========================================
# MOCK SEND COMMAND
# ==========================================
def send_command_to_arduino(packet, retries=MAX_RETRIES):
    global last_response
    logger.info(f"[MOCK] Sending packet: {packet.strip()}")
    time.sleep(0.05)  # Simulate small delay
    # Simulate always OK, or random error for testing
    if "INVALID" in packet:
        last_response = "INVALID_PACKET"
        logger.info("[MOCK] Arduino response: INVALID_PACKET")
        return {
            'success': False,
            'response': 'INVALID_PACKET',
            'error': 'Arduino rejected packet format (mock)'
        }
    else:
        last_response = "OK"
        logger.info("[MOCK] Arduino response: OK")
        return {
            'success': True,
            'response': 'OK',
            'error': None
        }

# ==========================================
# MOCK GET STATUS
# ==========================================
def get_serial_status():
    return {
        'connected': is_connected,
        'port': SERIAL_PORT,
        'baud_rate': BAUD_RATE,
        'last_response': last_response
    }
