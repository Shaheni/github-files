import cv2
import mediapipe as mp

# =========================
# MEDIAPIPE
# =========================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


# =========================
# PROCESS HAND
# =========================

def process_hand(img):

    img_rgb = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:

        for handLms in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                img,
                handLms,
                mp_hands.HAND_CONNECTIONS
            )

    return result, img