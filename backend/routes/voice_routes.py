from flask import Blueprint, jsonify

voice_bp = Blueprint('voice', __name__)

@voice_bp.route('/voice/status')
def voice_status():

    return jsonify({

        "voice": "active"
    })