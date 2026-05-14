def send_status(socketio, status):

    socketio.emit(
        "robot_status",
        status
    )