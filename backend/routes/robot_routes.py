from flask import (
    Blueprint,
    jsonify,
    request
)

from services.command_mapper import (
    process_robot_command
)

# ==========================================
# BLUEPRINT
# ==========================================

robot_routes = Blueprint(
    "robot_routes",
    __name__
)

# ==========================================
# ROBOT CONTROL API
# ==========================================

@robot_routes.route(
    "/api/control",
    methods=["POST"]
)
def control_robot():

    try:

        data = request.json

        result = process_robot_command(
            data
        )

        return jsonify({

            "status": "success",

            "result": result

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        })

# ==========================================
# START COMPUTER VISION
# ==========================================

@robot_routes.route(
    "/api/start_cv",
    methods=["POST"]
)
def start_cv():

    return jsonify({

        "status": "success",

        "message":
        "Computer Vision Started"

    })

# ==========================================
# TELEMETRY API
# ==========================================

@robot_routes.route(
    "/api/telemetry"
)
def telemetry():

    return jsonify({

        "cpu": "15%",
        "gpu": "0%",
        "status": "active"

    })