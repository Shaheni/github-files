from flask import Blueprint, jsonify
from controllers.ai_controller import ai_status

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/status')
def status():

    return jsonify(ai_status())