"""
Overlay rendering system — RETRO ARCADE EDITION.
Draws pixel-art HUD, photo booth frames, neon brackets, countdown, etc.
"""

import cv2
import numpy as np
import math
import time
import random


class OverlayRenderer:
    def __init__(self):
        self.scan_offset = 0
        self.pulse_phase = 0
        self.frame_count = 0
        self.star_positions = []  # for star frame

    def render(self, frame, face_data, motion_data, state):
        """Render all overlays onto the frame."""
        canvas = frame.copy()
        h, w = canvas.shape[:2]

        self.pulse_phase += 0.1
        self.frame_count += 1
        self.scan_offset = (self.scan_offset + 2) % h

        # ─── Photo booth frame (drawn first, behind everything) ───
        booth_frame = state.get("booth_frame", "none")
        if booth_frame != "none":
            self._draw_booth_frame(canvas, w, h, booth_frame)

        # ─── Scanline sweep ───────────────────────────
        if state.get("mode") == "scanning":
            self._draw_retro_scan(canvas, w, h)

        # ─── Face overlays ────────────────────────────
        if face_data and face_data["count"] > 0:
            self._draw_pixel_brackets(canvas, face_data)

        # ─── Motion zones ─────────────────────────────
        if motion_data and motion_data.get("detected"):
            self._draw_motion_regions(canvas, motion_data)

        # ─── Countdown ────────────────────────────────
        countdown = state.get("countdown")
        if countdown is not None and countdown > 0:
            self._draw_retro_countdown(canvas, countdown, w, h)

        # ─── Flash ────────────────────────────────────
        if state.get("flash", 0) > 0:
            self._draw_flash(canvas, state["flash"])

        # ─── Arcade HUD frame ─────────────────────────
        self._draw_arcade_border(canvas, w, h)

        # ─── Status bar ──────────────────────────────
        effect_name = state.get("effect_name", "None")
        mode = state.get("mode", "idle")
        score = state.get("score", 0)
        self._draw_arcade_status(canvas, w, h, mode, effect_name, score)

        return canvas

    # ─── RETRO SCAN ──────────────────────────────────────────────

    def _draw_retro_scan(self, canvas, w, h):
        """Sweeping neon green scanline with pixel stepping."""
        y = self.scan_offset
        # Main line
        cv2.line(canvas, (0, y), (w, y), (57, 255, 20), 2)
        # Faded trail
        for i in range(1, 6):
            trail_y = y - i * 3
            if 0 <= trail_y < h:
                alpha = 0.15 - (i * 0.025)
                overlay = canvas.copy()
                cv2.line(overlay, (0, trail_y), (w, trail_y), (57, 255, 20), 1)
                cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)

    # ─── PIXEL BRACKETS (face detection) ─────────────────────────

    def _draw_pixel_brackets(self, canvas, face_data):
        """Chunky pixel-art corner brackets around faces — arcade style."""
        pulse = abs(math.sin(self.pulse_phase))

        # Cycle neon colors
        colors = [
            (57, 255, 20),    # neon green
            (0, 255, 247),    # neon cyan
            (255, 45, 123),   # neon pink
        ]
        color_idx = (self.frame_count // 8) % len(colors)
        color = colors[color_idx]

        pixel = 4  # pixel block size for chunky look
        bracket_blocks = 6  # how many blocks per bracket arm

        for i, (cx, cy) in enumerate(face_data["centers"]):
            if i >= len(face_data["areas"]):
                break
            area = face_data["areas"][i]
            side = int(math.sqrt(area))
            half = side // 2
            x1, y1 = cx - half, cy - half
            x2, y2 = cx + half, cy + half

            # Draw pixel blocks for corners
            for b in range(bracket_blocks):
                offset = b * pixel

                # Top-left corner
                cv2.rectangle(canvas, (x1 + offset, y1), (x1 + offset + pixel, y1 + pixel), color, -1)
                cv2.rectangle(canvas, (x1, y1 + offset), (x1 + pixel, y1 + offset + pixel), color, -1)

                # Top-right corner
                cv2.rectangle(canvas, (x2 - offset - pixel, y1), (x2 - offset, y1 + pixel), color, -1)
                cv2.rectangle(canvas, (x2 - pixel, y1 + offset), (x2, y1 + offset + pixel), color, -1)

                # Bottom-left corner
                cv2.rectangle(canvas, (x1 + offset, y2 - pixel), (x1 + offset + pixel, y2), color, -1)
                cv2.rectangle(canvas, (x1, y2 - offset - pixel), (x1 + pixel, y2 - offset), color, -1)

                # Bottom-right corner
                cv2.rectangle(canvas, (x2 - offset - pixel, y2 - pixel), (x2 - offset, y2), color, -1)
                cv2.rectangle(canvas, (x2 - pixel, y2 - offset - pixel), (x2, y2 - offset), color, -1)

            # Crosshair (pixel style)
            cross = 6
            for c in range(-cross, cross + 1):
                px, py = cx + c * 2, cy
                cv2.rectangle(canvas, (px, py), (px + 2, py + 2), color, -1)
                px, py = cx, cy + c * 2
                cv2.rectangle(canvas, (px, py), (px + 2, py + 2), color, -1)

            # "DETECTED" text above face
            if pulse > 0.5:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(canvas, "DETECTED", (x1, y1 - 10), font, 0.5, color, 1, cv2.LINE_AA)

    # ─── MOTION REGIONS ──────────────────────────────────────────

    def _draw_motion_regions(self, canvas, motion_data):
        """Draw motion with neon cyan dashed outlines."""
        color = (0, 255, 247)
        for (x, y, w, h) in motion_data.get("regions", []):
            # Dashed rectangle (draw segments)
            dash_len = 8
            gap = 4
            for side_x in range(x, x + w, dash_len + gap):
                end_x = min(side_x + dash_len, x + w)
                cv2.line(canvas, (side_x, y), (end_x, y), color, 2)
                cv2.line(canvas, (side_x, y + h), (end_x, y + h), color, 2)
            for side_y in range(y, y + h, dash_len + gap):
                end_y = min(side_y + dash_len, y + h)
                cv2.line(canvas, (x, side_y), (x, end_y), color, 2)
                cv2.line(canvas, (x + w, side_y), (x + w, end_y), color, 2)

    # ─── COUNTDOWN ───────────────────────────────────────────────

    def _draw_retro_countdown(self, canvas, count, w, h):
        """Big blocky pixel countdown number with neon glow."""
        text = str(int(count))
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 8
        thickness = 16

        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        tx = (w - text_size[0]) // 2
        ty = (h + text_size[1]) // 2

        # Outer glow (neon pink)
        for r in range(4, 0, -1):
            glow_overlay = canvas.copy()
            cv2.putText(glow_overlay, text, (tx, ty), font, scale,
                        (255, 45, 123), thickness + r * 6, cv2.LINE_AA)
            alpha = 0.08 * r
            cv2.addWeighted(glow_overlay, alpha, canvas, 1 - alpha, 0, canvas)

        # Main number (neon yellow)
        cv2.putText(canvas, text, (tx, ty), font, scale,
                    (255, 230, 0), thickness, cv2.LINE_AA)

        # Inner bright core
        cv2.putText(canvas, text, (tx, ty), font, scale,
                    (255, 255, 255), thickness // 2, cv2.LINE_AA)

    # ─── FLASH ───────────────────────────────────────────────────

    def _draw_flash(self, canvas, intensity):
        """Neon flash — white with slight green tint."""
        flash_color = np.full_like(canvas, [240, 255, 240])
        alpha = min(intensity, 1.0)
        cv2.addWeighted(flash_color, alpha, canvas, 1 - alpha, 0, canvas)

    # ─── ARCADE BORDER ───────────────────────────────────────────

    def _draw_arcade_border(self, canvas, w, h):
        """Pixel-art arcade cabinet border with corner decorations."""
        color = (57, 255, 20)  # neon green
        dim = (20, 80, 10)     # dim version

        pixel = 3
        corner_size = 8  # blocks

        # Draw pixel corners
        for b in range(corner_size):
            # Top-left
            cv2.rectangle(canvas, (b * pixel, 0), ((b + 1) * pixel, pixel), dim, -1)
            cv2.rectangle(canvas, (0, b * pixel), (pixel, (b + 1) * pixel), dim, -1)
            # Top-right
            cv2.rectangle(canvas, (w - (b + 1) * pixel, 0), (w - b * pixel, pixel), dim, -1)
            cv2.rectangle(canvas, (w - pixel, b * pixel), (w, (b + 1) * pixel), dim, -1)
            # Bottom-left
            cv2.rectangle(canvas, (b * pixel, h - pixel), ((b + 1) * pixel, h), dim, -1)
            cv2.rectangle(canvas, (0, h - (b + 1) * pixel), (pixel, h - b * pixel), dim, -1)
            # Bottom-right
            cv2.rectangle(canvas, (w - (b + 1) * pixel, h - pixel), (w - b * pixel, h), dim, -1)
            cv2.rectangle(canvas, (w - pixel, h - (b + 1) * pixel), (w, h - b * pixel), dim, -1)

        # Bright corner dots (4 corners)
        dot_color = color if (self.frame_count // 15) % 2 == 0 else (0, 255, 247)
        dot_size = pixel * 2
        cv2.rectangle(canvas, (0, 0), (dot_size, dot_size), dot_color, -1)
        cv2.rectangle(canvas, (w - dot_size, 0), (w, dot_size), dot_color, -1)
        cv2.rectangle(canvas, (0, h - dot_size), (dot_size, h), dot_color, -1)
        cv2.rectangle(canvas, (w - dot_size, h - dot_size), (w, h), dot_color, -1)

    # ─── STATUS BAR ──────────────────────────────────────────────

    def _draw_arcade_status(self, canvas, w, h, mode, effect_name, score):
        """Arcade-style bottom status bar with score display."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        bar_h = 28

        # Bar background
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, h - bar_h), (w, h), (13, 13, 26), -1)
        cv2.addWeighted(overlay, 0.85, canvas, 0.15, 0, canvas)

        # Top border of bar (neon line)
        cv2.line(canvas, (0, h - bar_h), (w, h - bar_h), (57, 255, 20), 1)

        # Mode
        mode_text = f"MODE:{mode.upper()}"
        cv2.putText(canvas, mode_text, (8, h - 8), font, 0.4,
                    (57, 255, 20), 1, cv2.LINE_AA)

        # Score
        score_text = f"SCORE:{score:06d}"
        score_size = cv2.getTextSize(score_text, font, 0.4, 1)[0]
        cv2.putText(canvas, score_text, (w // 2 - score_size[0] // 2, h - 8),
                    font, 0.4, (255, 230, 0), 1, cv2.LINE_AA)

        # Effect
        fx_text = f"FX:{effect_name.upper()}"
        fx_size = cv2.getTextSize(fx_text, font, 0.4, 1)[0]
        cv2.putText(canvas, fx_text, (w - fx_size[0] - 8, h - 8),
                    font, 0.4, (0, 255, 247), 1, cv2.LINE_AA)

    # ─── PHOTO BOOTH FRAMES ─────────────────────────────────────

    def _draw_booth_frame(self, canvas, w, h, frame_type):
        """Draw decorative photo booth frames around the feed."""
        if frame_type == "hearts":
            self._draw_hearts_frame(canvas, w, h)
        elif frame_type == "stars":
            self._draw_stars_frame(canvas, w, h)
        elif frame_type == "arcade":
            self._draw_arcade_deco_frame(canvas, w, h)
        elif frame_type == "glitch_frame":
            self._draw_glitch_border(canvas, w, h)
        elif frame_type == "rainbow":
            self._draw_rainbow_frame(canvas, w, h)

    def _draw_hearts_frame(self, canvas, w, h):
        """Pixel hearts around the border."""
        color = (255, 45, 123)
        pixel = 3
        spacing = 40
        offset = (self.frame_count // 2) % spacing

        for x in range(-offset, w + spacing, spacing):
            self._draw_pixel_heart(canvas, x, 8, pixel, color)
            self._draw_pixel_heart(canvas, x + spacing // 2, h - 20, pixel, color)

        for y in range(-offset, h + spacing, spacing):
            self._draw_pixel_heart(canvas, 8, y, pixel, color)
            self._draw_pixel_heart(canvas, w - 20, y + spacing // 2, pixel, color)

    def _draw_pixel_heart(self, canvas, cx, cy, px, color):
        """Draw a tiny pixel-art heart."""
        # Heart pattern (relative to cx, cy)
        pattern = [
            (1, 0), (2, 0), (4, 0), (5, 0),
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (2, 4), (3, 4), (4, 4),
            (3, 5),
        ]
        h_canvas, w_canvas = canvas.shape[:2]
        for dx, dy in pattern:
            x1 = cx + dx * px
            y1 = cy + dy * px
            if 0 <= x1 < w_canvas - px and 0 <= y1 < h_canvas - px:
                cv2.rectangle(canvas, (x1, y1), (x1 + px, y1 + px), color, -1)

    def _draw_stars_frame(self, canvas, w, h):
        """Twinkling pixel stars around the border."""
        color_a = (255, 230, 0)   # yellow
        color_b = (255, 255, 255) # white
        pixel = 2

        # Generate consistent star positions
        np.random.seed(42)
        num_stars = 30
        for i in range(num_stars):
            side = i % 4
            if side == 0:  # top
                sx = np.random.randint(10, w - 10)
                sy = np.random.randint(4, 18)
            elif side == 1:  # bottom
                sx = np.random.randint(10, w - 10)
                sy = np.random.randint(h - 18, h - 4)
            elif side == 2:  # left
                sx = np.random.randint(4, 18)
                sy = np.random.randint(10, h - 10)
            else:  # right
                sx = np.random.randint(w - 18, w - 4)
                sy = np.random.randint(10, h - 10)

            # Twinkle effect
            visible = ((self.frame_count + i * 7) // 5) % 3 != 0
            if visible:
                color = color_a if i % 2 == 0 else color_b
                size = pixel if ((self.frame_count + i) // 8) % 2 == 0 else pixel * 2
                cv2.rectangle(canvas, (sx, sy), (sx + size, sy + size), color, -1)
                # Cross shape for bigger stars
                if size > pixel:
                    cv2.rectangle(canvas, (sx - pixel, sy + pixel), (sx, sy + pixel * 2), color, -1)
                    cv2.rectangle(canvas, (sx + size, sy + pixel), (sx + size + pixel, sy + pixel * 2), color, -1)

    def _draw_arcade_deco_frame(self, canvas, w, h):
        """Arcade cabinet style decorative border with chevrons."""
        colors = [(57, 255, 20), (0, 255, 247), (255, 230, 0)]
        pixel = 3
        offset = (self.frame_count // 3) % 18

        # Top chevron pattern
        for i in range(0, w, 18):
            x = i + offset
            ci = (i // 18) % len(colors)
            color = colors[ci]
            if x < w - 12:
                # Up chevron
                cv2.rectangle(canvas, (x + 4, 2), (x + 7, 5), color, -1)
                cv2.rectangle(canvas, (x + 1, 5), (x + 4, 8), color, -1)
                cv2.rectangle(canvas, (x + 7, 5), (x + 10, 8), color, -1)

        # Bottom chevron pattern (inverted)
        for i in range(0, w, 18):
            x = i - offset + 9
            ci = (i // 18) % len(colors)
            color = colors[ci]
            if 0 < x < w - 12:
                cv2.rectangle(canvas, (x + 4, h - 5), (x + 7, h - 2), color, -1)
                cv2.rectangle(canvas, (x + 1, h - 8), (x + 4, h - 5), color, -1)
                cv2.rectangle(canvas, (x + 7, h - 8), (x + 10, h - 5), color, -1)

    def _draw_glitch_border(self, canvas, w, h):
        """Randomly flickering border segments."""
        colors = [(255, 45, 123), (0, 255, 247), (57, 255, 20)]

        for _ in range(8):
            side = random.randint(0, 3)
            length = random.randint(20, 80)
            color = random.choice(colors)
            thick = random.randint(2, 5)

            if side == 0:  # top
                x = random.randint(0, w - length)
                cv2.rectangle(canvas, (x, 0), (x + length, thick), color, -1)
            elif side == 1:  # bottom
                x = random.randint(0, w - length)
                cv2.rectangle(canvas, (x, h - thick), (x + length, h), color, -1)
            elif side == 2:  # left
                y = random.randint(0, h - length)
                cv2.rectangle(canvas, (0, y), (thick, y + length), color, -1)
            else:  # right
                y = random.randint(0, h - length)
                cv2.rectangle(canvas, (w - thick, y), (w, y + length), color, -1)

    def _draw_rainbow_frame(self, canvas, w, h):
        """Animated rainbow border cycling through colors."""
        rainbow = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 255, 255), (0, 127, 255), (127, 0, 255)
        ]
        segment = 6
        offset = self.frame_count % (len(rainbow) * segment)

        thick = 4
        for x in range(0, w, segment):
            ci = ((x + offset) // segment) % len(rainbow)
            color = rainbow[ci]
            cv2.rectangle(canvas, (x, 0), (x + segment, thick), color, -1)
            cv2.rectangle(canvas, (x, h - thick), (x + segment, h), color, -1)

        for y in range(0, h, segment):
            ci = ((y + offset) // segment) % len(rainbow)
            color = rainbow[ci]
            cv2.rectangle(canvas, (0, y), (thick, y + segment), color, -1)
            cv2.rectangle(canvas, (w - thick, y), (w, y + segment), color, -1)