"""
Camera capture and vision pipeline.
Coordinates face detection, motion tracking, and frame processing.
"""

import cv2
from vision.face import FaceDetector
from vision.hands import MotionTracker
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT


class Camera:
    def __init__(self, camera_index=CAMERA_INDEX):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        self.face_detector = FaceDetector()
        self.motion_tracker = MotionTracker()

        self.scan_offset = 0
        self.frame_count = 0

    def get_frame(self):
        """
        Capture and process one frame.
        Returns: (frame_rgb, face_data, motion_data) or (None, None, None)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None

        self.frame_count += 1

        # Mirror the frame for natural interaction
        frame = cv2.flip(frame, 1)

        # ─── Face Detection ───────────────────────────
        faces = self.face_detector.detect(frame)
        face_data = self.face_detector.analyze(faces)

        # ─── Motion Detection ─────────────────────────
        h, w = frame.shape[:2]
        has_motion, regions = self.motion_tracker.detect(frame)
        gesture_zone = self.motion_tracker.get_gesture_zone(w, h)

        motion_data = {
            "detected": has_motion,
            "regions": regions,
            "zone": gesture_zone,
        }

        # ─── Convert to RGB for Qt ────────────────────
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame_rgb, face_data, motion_data

    def capture_raw(self):
        """Capture a clean frame without any overlays (for saving photos)."""
        ret, frame = self.cap.read()
        if not ret:
            return None
        frame = cv2.flip(frame, 1)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def release(self):
        self.cap.release()