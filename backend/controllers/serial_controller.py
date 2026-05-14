import serial
import time

from backend.config.settings import (
    SERIAL_PORT,
    BAUD_RATE
)

class SerialController:

    def __init__(self):

        self.arduino = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        )

        time.sleep(2)

        print("✅ Arduino Connected")

    def send(self, packet):

        self.arduino.write(
            packet.encode()
        )

        print(f"📤 SENT: {packet}")

    def read(self):

        if self.arduino.in_waiting:

            return self.arduino.readline().decode().strip()

        return None