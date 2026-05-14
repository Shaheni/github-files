import cv2

def start_camera():

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        cv2.imshow("Robot Camera", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()

    cv2.destroyAllWindows()