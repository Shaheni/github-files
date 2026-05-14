import serial
import time

# ==========================================
# SERIAL CONFIGURATION
# ==========================================

SERIAL_PORT = "COM5"
BAUD_RATE = 115200

arduino = None

# ==========================================
# CONNECT TO ARDUINO
# ==========================================

try:

    arduino = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=1
    )

    time.sleep(2)

    print("Arduino Connected Successfully")

except Exception as e:

    print("Arduino Connection Failed")
    print(e)

# ==========================================
# SEND DATA TO ARDUINO
# ==========================================

def send_data_to_arduino(data):

    global arduino

    if arduino:

        arduino.write(
            data.encode()
        )

        print(f"Sent -> {data}")

    else:

        print("Arduino Not Connected")