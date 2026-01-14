import cv2
import os

class FaceDetector:
    def __init__(self) :
        cascade_path = os.path.join(
            os.path.dirname(cv2.__file__), 
            "data",
            "haarcascade_frontalface_default.xml"
        )
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            raise RuntimeError("Failed to load face cascade")
        

    def detect(self, frame) :
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80,80)
        )

        return faces