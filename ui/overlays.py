"""
Overlay rendering system.
Draws HUD elements, face brackets, motion zones, countdown, etc.
All drawing happens on a copy of the frame — never mutates the original.
"""

import cv2
import numpy as np
import math
import time


class OverlayRenderer:
    def __init__(self):
        self.scan_offset = 0
        self.pulse_phase = 0
        self.particle_positions = []

    def render(self, frame, face_data, motion_data, state):
        """
        Render all overlays onto the frame.
        state dict should contain: mode, countdown, effect_name, etc.
        """
        canvas = frame.copy()
        h, w = canvas.shape[:2]

        self.pulse_phase += 0.08
        self.scan_offset = (self.scan_offset + 3) % h

        # ─── Ambient scanline (subtle) ────────────────
        if state.get("mode") == "scanning":
            self._draw_scan_line(canvas, w, h)

        # ─── Face overlays ────────────────────────────
        if face_data and face_data["count"] > 0:
            self._draw_face_brackets(canvas, face_data)

        # ─── Motion zone indicator ────────────────────
        if motion_data and motion_data.get("detected"):
            self._draw_motion_regions(canvas, motion_data)

        # ─── Countdown overlay ────────────────────────
        countdown = state.get("countdown")
        if countdown is not None and countdown > 0:
            self._draw_countdown(canvas, countdown, w, h)

        # ─── Flash overlay ────────────────────────────
        if state.get("flash", 0) > 0:
            self._draw_flash(canvas, state["flash"])

        # ─── Corner brackets (HUD frame) ──────────────
        self._draw_hud_frame(canvas, w, h)

        # ─── Status bar at bottom ─────────────────────
        effect_name = state.get("effect_name", "None")
        mode = state.get("mode", "idle")
        self._draw_status_bar(canvas, w, h, mode, effect_name)

        return canvas

    def _draw_scan_line(self, canvas, w, h):
        """Sweeping horizontal scan line."""
        y = self.scan_offset
        alpha = 0.3
        overlay = canvas.copy()
        cv2.line(overlay, (0, y), (w, y), (0, 255, 136), 1)
        # Glow effect: draw wider transparent lines
        cv2.line(overlay, (0, y-1), (w, y-1), (0, 255, 136), 1)
        cv2.line(overlay, (0, y+1), (w, y+1), (0, 255, 136), 1)
        cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)

    def _draw_face_brackets(self, canvas, face_data):
        """Draw animated corner brackets around detected faces."""
        pulse = abs(math.sin(self.pulse_phase))
        green = (0, int(200 + 55 * pulse), int(100 + 36 * pulse))
        bracket_len = 20
        thickness = 2

        for i, (cx, cy) in enumerate(face_data["centers"]):
            if i >= len(face_data["areas"]):
                break
            area = face_data["areas"][i]
            side = int(math.sqrt(area))
            half = side // 2
            x1, y1 = cx - half, cy - half
            x2, y2 = cx + half, cy + half

            # Corner brackets (not full rectangle — looks way cooler)
            # Top-left
            cv2.line(canvas, (x1, y1), (x1 + bracket_len, y1), green, thickness)
            cv2.line(canvas, (x1, y1), (x1, y1 + bracket_len), green, thickness)
            # Top-right
            cv2.line(canvas, (x2, y1), (x2 - bracket_len, y1), green, thickness)
            cv2.line(canvas, (x2, y1), (x2, y1 + bracket_len), green, thickness)
            # Bottom-left
            cv2.line(canvas, (x1, y2), (x1 + bracket_len, y2), green, thickness)
            cv2.line(canvas, (x1, y2), (x1, y2 - bracket_len), green, thickness)
            # Bottom-right
            cv2.line(canvas, (x2, y2), (x2 - bracket_len, y2), green, thickness)
            cv2.line(canvas, (x2, y2), (x2, y2 - bracket_len), green, thickness)

            # Center crosshair (tiny)
            cross_size = 5
            cv2.line(canvas, (cx - cross_size, cy), (cx + cross_size, cy), green, 1)
            cv2.line(canvas, (cx, cy - cross_size), (cx, cy + cross_size), green, 1)

    def _draw_motion_regions(self, canvas, motion_data):
        """Draw motion bounding boxes with cyan tint."""
        for (x, y, w, h) in motion_data.get("regions", []):
            # Semi-transparent cyan box
            overlay = canvas.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 229, 255), 2)
            cv2.addWeighted(overlay, 0.6, canvas, 0.4, 0, canvas)

    def _draw_countdown(self, canvas, count, w, h):
        """Big centered countdown number with glow."""
        text = str(int(count))
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 6
        thickness = 12

        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        tx = (w - text_size[0]) // 2
        ty = (h + text_size[1]) // 2

        # Glow layers
        for i, alpha_mult in enumerate([0.15, 0.3, 0.6]):
            glow_thick = thickness + (3 - i) * 8
            overlay = canvas.copy()
            cv2.putText(overlay, text, (tx, ty), font, scale,
                        (0, 255, 136), glow_thick, cv2.LINE_AA)
            cv2.addWeighted(overlay, alpha_mult, canvas, 1 - alpha_mult, 0, canvas)

        # Main text
        cv2.putText(canvas, text, (tx, ty), font, scale,
                    (255, 255, 255), thickness, cv2.LINE_AA)

    def _draw_flash(self, canvas, intensity):
        """White flash overlay for photo capture."""
        white = np.full_like(canvas, 255)
        alpha = min(intensity, 1.0)
        cv2.addWeighted(white, alpha, canvas, 1 - alpha, 0, canvas)

    def _draw_hud_frame(self, canvas, w, h):
        """Subtle corner brackets around the entire viewport."""
        color = (40, 40, 40)
        length = 40
        t = 1

        # Top-left
        cv2.line(canvas, (10, 10), (10 + length, 10), color, t)
        cv2.line(canvas, (10, 10), (10, 10 + length), color, t)
        # Top-right
        cv2.line(canvas, (w - 10, 10), (w - 10 - length, 10), color, t)
        cv2.line(canvas, (w - 10, 10), (w - 10, 10 + length), color, t)
        # Bottom-left
        cv2.line(canvas, (10, h - 10), (10 + length, h - 10), color, t)
        cv2.line(canvas, (10, h - 10), (10, h - 10 - length), color, t)
        # Bottom-right
        cv2.line(canvas, (w - 10, h - 10), (w - 10 - length, h - 10), color, t)
        cv2.line(canvas, (w - 10, h - 10), (w - 10, h - 10 - length), color, t)

    def _draw_status_bar(self, canvas, w, h, mode, effect_name):
        """Bottom status bar with mode and effect info."""
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Semi-transparent bar
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, h - 32), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, canvas, 0.4, 0, canvas)

        # Mode indicator
        mode_text = f"MODE: {mode.upper()}"
        cv2.putText(canvas, mode_text, (12, h - 10), font, 0.4,
                    (0, 255, 136), 1, cv2.LINE_AA)

        # Effect indicator
        effect_text = f"FX: {effect_name.upper()}"
        text_size = cv2.getTextSize(effect_text, font, 0.4, 1)[0]
        cv2.putText(canvas, effect_text, (w - text_size[0] - 12, h - 10),
                    font, 0.4, (0, 229, 255), 1, cv2.LINE_AA)