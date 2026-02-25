"""
Face detection using Haar cascades.
Single responsibility: detect faces and return metadata.
"""

import cv2
import os
from config import FACE_SCALE_FACTOR, FACE_MIN_NEIGHBORS, FACE_MIN_SIZE


class FaceDetector:
    def __init__(self):
        cascade_path = os.path.join(
            os.path.dirname(cv2.__file__),
            "data",
            "haarcascade_frontalface_default.xml"
        )
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            raise RuntimeError("Failed to load face cascade classifier")

        self.prev_faces = None
        self.stable_count = 0

    def detect(self, frame):
        """Detect faces in frame. Returns list of (x, y, w, h) tuples."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)  # better detection in varied lighting

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=FACE_SCALE_FACTOR,
            minNeighbors=FACE_MIN_NEIGHBORS,
            minSize=FACE_MIN_SIZE
        )

        return faces

    def analyze(self, faces):
        """Analyze detected faces for stability and position data."""
        data = {
            "count": len(faces),
            "centers": [],
            "areas": [],
            "stable": False,
            "stable_frames": self.stable_count,
            "primary": None,  # largest face
        }

        largest_area = 0
        for (x, y, w, h) in faces:
            cx, cy = x + w // 2, y + h // 2
            area = w * h
            data["centers"].append((cx, cy))
            data["areas"].append(area)
            if area > largest_area:
                largest_area = area
                data["primary"] = {"x": x, "y": y, "w": w, "h": h, "cx": cx, "cy": cy}

        # Stability tracking
        if self.prev_faces is not None and len(faces) == len(self.prev_faces):
            self.stable_count += 1
            data["stable"] = self.stable_count > 5
        else:
            self.stable_count = 0

        data["stable_frames"] = self.stable_count
        self.prev_faces = faces
        return data