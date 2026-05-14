from flask import Blueprint, jsonify

telemetry_bp = Blueprint('telemetry', __name__)

@telemetry_bp.route('/telemetry')
def telemetry():

    return jsonify({

        "battery": 87,
        "temperature": 35,
        "speed": 12
    })