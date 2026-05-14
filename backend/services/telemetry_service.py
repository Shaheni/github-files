import random

def get_telemetry_data():

    telemetry = {

        "battery":
        random.randint(70, 100),

        "temperature":
        random.randint(30, 45),

        "speed":
        random.randint(0, 20),

        "latency":
        random.randint(1, 10)
    }

    return telemetry