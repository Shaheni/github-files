from backend.services.speech_service import (
    listen
)

from backend.services.command_mapper import (
    VOICE_COMMANDS
)

from backend.controllers.robot_controller import (
    RobotController
)

robot = RobotController()

def start_voice_control():

    while True:

        text = listen()

        if not text:
            continue

        if text == "exit":
            break

        if text in VOICE_COMMANDS:

            angles = VOICE_COMMANDS[text]

            robot.move(angles)

            print(f"✅ ACTION: {angles}")

        else:

            print("❌ Unknown Command")