"""
Motion-based hand/gesture detection.
Uses frame differencing to detect significant movement regions.

Note: This is motion detection, not true hand recognition.
For real hand tracking, integrate MediaPipe (see README).
"""

import cv2
import numpy as np
from config import MOTION_AREA_THRESHOLD


class MotionTracker:
    def __init__(self):
        self.prev_gray = None
        self.kernel = np.ones((5, 5), np.uint8)
        self.motion_regions = []

    def detect(self, frame):
        """
        Detect motion regions in frame.
        Returns: (has_motion: bool, regions: list of (x, y, w, h))
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (15, 15), 0)

        if self.prev_gray is None:
            self.prev_gray = gray
            return False, []

        # Frame difference
        diff = cv2.absdiff(self.prev_gray, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, self.kernel, iterations=2)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        self.motion_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MOTION_AREA_THRESHOLD:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            self.motion_regions.append((x, y, w, h))

        self.prev_gray = gray
        return len(self.motion_regions) > 0, self.motion_regions

    def get_gesture_zone(self, frame_width, frame_height):
        """
        Map motion regions to gesture zones.
        Divides frame into a 3x3 grid for zone-based interaction.

        Returns zone name: 'top-left', 'center', 'bottom-right', etc.
        """
        if not self.motion_regions:
            return None

        # Use the largest motion region
        largest = max(self.motion_regions, key=lambda r: r[2] * r[3])
        cx = largest[0] + largest[2] // 2
        cy = largest[1] + largest[3] // 2

        # Map to 3x3 grid
        col = "left" if cx < frame_width / 3 else "right" if cx > 2 * frame_width / 3 else "center"
        row = "top" if cy < frame_height / 3 else "bottom" if cy > 2 * frame_height / 3 else "middle"

        if row == "middle" and col == "center":
            return "center"
        return f"{row}-{col}"