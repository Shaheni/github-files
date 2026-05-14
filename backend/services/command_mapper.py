from controllers.robot_controller import (
    send_servo_command
)

# ==========================================
# PROCESS COMMAND
# ==========================================

def process_robot_command(data):

    try:

        servo1 = data.get("servo1", 90)
        servo2 = data.get("servo2", 90)
        servo3 = data.get("servo3", 90)
        servo4 = data.get("servo4", 90)
        servo5 = data.get("servo5", 90)
        servo6 = data.get("servo6", 90)

        command = (
            f"{servo1},"
            f"{servo2},"
            f"{servo3},"
            f"{servo4},"
            f"{servo5},"
            f"{servo6}\n"
        )

        send_servo_command(command)

        return {
            "success": True,
            "command": command
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }