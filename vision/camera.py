import cv2
import os

class Camera :
    def __init__(self, camera_index = 0) :
        self.cap = cv2.VideoCapture(camera_index)

        #loading haar cascade for face detection
        # self.face_cascade = cv2.CascadeClassifier(
        #     cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        # )
        cascade_path = os.path.join (
            os.path.dirname(cv2.__file__), 
            "data", 
            "haarcascade_frontalface_default.xml"
        )

        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.scan_offset = 0 #for scanning line animation

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            scan_y = y + (self.scan_offset % h)
            cv2.line(frame, (x, scan_y), (x + w, scan_y), (0, 255, 0), 1)

        self.scan_offset += 5

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame, len(faces) > 0

    
    def release(self) :
        self.cap.release()
