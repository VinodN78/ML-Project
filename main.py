import cv2
import dlib
import numpy as np
import pyautogui
import time

# Initialize dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

cap = cv2.VideoCapture(0)


def eye_aspect_ratio(eye):
    """Calculate the Eye Aspect Ratio (EAR) to detect blink."""
    vertical1 = np.linalg.norm(eye[1] - eye[5])
    vertical2 = np.linalg.norm(eye[2] - eye[4])
    horizontal = np.linalg.norm(eye[0] - eye[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)


def calibrate():
    """Calibration function to set reference positions."""
    positions = ["center", "top-left", "top-right", "bottom-left", "bottom-right"]
    calibrated_positions = {}

    for position in positions:
        input(f"Please look at the {position} of the screen and press Enter...")
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)  # Mirror the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        if faces:
            landmarks = predictor(gray, faces[0])
            nose_position = (landmarks.part(33).x, landmarks.part(33).y)
            calibrated_positions[position] = nose_position
        else:
            print("Face not detected during calibration.")
            return None

    return calibrated_positions


calibration_data = calibrate()

EAR_THRESHOLD = 0.25
EYE_CONSECUTIVE_FRAMES = 6
DOUBLE_BLINK_DELAY = 0.2
BLINK_COOLDOWN = 1  # seconds

frame_counter = 0
blink_timestamps = []

if calibration_data:
    try:

        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)  # Mirror the frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)

                # Movement based on the nose position
                nose_position = (landmarks.part(33).x, landmarks.part(33).y)
                diff_x = nose_position[0] - calibration_data["center"][0]
                diff_y = nose_position[1] - calibration_data["center"][1]
                pyautogui.moveRel(diff_x, diff_y, duration=0.1)

                # Calculate EAR for blink detection
                left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0

                if ear < EAR_THRESHOLD:
                    frame_counter += 1
                else:
                    if frame_counter >= EYE_CONSECUTIVE_FRAMES:
                        blink_timestamps.append(time.time())
                        frame_counter = 0

                # Check if double blink happened within DOUBLE_BLINK_DELAY
                if len(blink_timestamps) > 1 and blink_timestamps[-1] - blink_timestamps[-2] <= DOUBLE_BLINK_DELAY:
                    pyautogui.click(button='right')
                    blink_timestamps = []  # reset
                elif len(blink_timestamps) == 1 and time.time() - blink_timestamps[0] > DOUBLE_BLINK_DELAY:
                    pyautogui.click(button='left')
                    blink_timestamps = []  # reset

            cv2.imshow('Blink Detection and Cursor Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass

    cap.release()
    cv2.destroyAllWindows()
