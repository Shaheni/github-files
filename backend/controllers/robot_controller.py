from services.serial_service import (
    send_data_to_arduino
)

# ==========================================
# SEND SERVO COMMAND
# ==========================================

def send_servo_command(command):

    send_data_to_arduino(command)

    return {
        "status": "sent",
        "command": command
    }