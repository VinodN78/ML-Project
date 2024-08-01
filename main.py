from headmouse import Headmouse
import cv2

if __name__ == "__main__":
    predictor_path = "D:/ITC/shape_predictor_68_face_landmarks.dat"
    h = Headmouse(predictor_path=predictor_path)
    while True:
        h.refresh()
        h.show_image()
        key = cv2.waitKey(1)
        if key == 27: #press escape
            h.destroy_window()
            h.quit()
            break
        if key == 32: #press spacebar
            h.calibrate()
            print("calibrated")
