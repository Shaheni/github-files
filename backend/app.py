from flask import (
    Flask,
    send_from_directory
)

from flask_cors import CORS

from flask_socketio import SocketIO

from routes.robot_routes import (
    robot_routes
)

import os

# ==========================================
# FRONTEND PATH
# ==========================================

frontend_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend"
)

# ==========================================
# FLASK APP
# ==========================================

app = Flask(

    __name__,

    static_folder=frontend_path,

    static_url_path=""
)

CORS(app)

socketio = SocketIO(

    app,

    cors_allowed_origins="*"
)

# ==========================================
# REGISTER ROUTES
# ==========================================

app.register_blueprint(
    robot_routes
)

# ==========================================
# SERVE FRONTEND
# ==========================================

@app.route("/")
def serve_frontend():

    return send_from_directory(
        frontend_path,
        "index.html"
    )

# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    socketio.run(

        app,

        host="127.0.0.1",

        port=5050,

        debug=True
    )