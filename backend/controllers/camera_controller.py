import cv2

camera = cv2.VideoCapture(0)

def get_camera_status():

    success, frame = camera.read()

    return success