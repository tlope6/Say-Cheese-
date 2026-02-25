"""
Say Cheese! — Main Window
A fun, interactive, aesthetically pleasing camera experience.
"""

import os
import time
import math
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QSizePolicy,
    QScrollArea, QGridLayout
)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QLinearGradient, QIcon, QCursor

from vision.camera import Camera
from vision.effects import apply_effect
from ui.overlays import OverlayRenderer
from data.database import EventLogger
from config import COLORS, EFFECTS, COUNTDOWN_SECONDS, CAMERA_FPS, PHOTO_SAVE_DIR


# ═══════════════════════════════════════════════════════════════════
#  STYLESHEET
# ═══════════════════════════════════════════════════════════════════

STYLESHEET = f"""
    * {{
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    }}

    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}

    QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
    }}

    QLabel#title {{
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 3px;
        color: {COLORS['text_primary']};
    }}

    QLabel#subtitle {{
        font-size: 11px;
        font-weight: 400;
        color: {COLORS['text_dim']};
        letter-spacing: 1px;
    }}

    QLabel#status {{
        font-size: 12px;
        font-weight: 500;
        color: {COLORS['accent_green']};
        padding: 6px 14px;
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        background-color: {COLORS['bg_elevated']};
    }}

    QLabel#cameraFeed {{
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        background-color: #000000;
    }}

    QPushButton {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        color: {COLORS['text_primary']};
        background-color: {COLORS['bg_elevated']};
        letter-spacing: 0.5px;
    }}

    QPushButton:hover {{
        background-color: {COLORS['bg_card']};
        border-color: {COLORS['accent_green']};
        color: {COLORS['accent_green']};
    }}

    QPushButton:pressed {{
        background-color: {COLORS['bg_dark']};
    }}

    QPushButton#captureBtn {{
        font-size: 14px;
        padding: 12px 28px;
        border-radius: 24px;
        border: 2px solid {COLORS['accent_green']};
        color: {COLORS['accent_green']};
        background-color: rgba(0, 255, 136, 0.05);
        letter-spacing: 2px;
    }}

    QPushButton#captureBtn:hover {{
        background-color: rgba(0, 255, 136, 0.15);
        border-color: {COLORS['accent_green']};
    }}

    QPushButton#effectBtn {{
        border-radius: 20px;
        min-width: 40px;
        min-height: 40px;
        max-width: 40px;
        max-height: 40px;
        padding: 0;
        font-size: 16px;
    }}

    QPushButton#effectBtnActive {{
        border-radius: 20px;
        min-width: 40px;
        min-height: 40px;
        max-width: 40px;
        max-height: 40px;
        padding: 0;
        font-size: 16px;
        border: 2px solid {COLORS['accent_cyan']};
        background-color: rgba(0, 229, 255, 0.12);
        color: {COLORS['accent_cyan']};
    }}

    QFrame#separator {{
        background-color: {COLORS['border']};
        max-height: 1px;
    }}

    QFrame#sidePanel {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 12px;
    }}

    QLabel#galleryThumb {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['bg_dark']};
    }}

    QLabel#sectionTitle {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        color: {COLORS['text_dim']};
    }}

    QLabel#eventLog {{
        font-size: 10px;
        color: {COLORS['text_muted']};
        font-family: 'Consolas', 'SF Mono', monospace;
    }}

    QLabel#statsLabel {{
        font-size: 20px;
        font-weight: 700;
        color: {COLORS['accent_cyan']};
    }}

    QLabel#statsCaption {{
        font-size: 9px;
        font-weight: 600;
        letter-spacing: 1.5px;
        color: {COLORS['text_dim']};
    }}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ─── Core State ──────────────────────────────
        self.face_present = False
        self.hands_present = False
        self.current_effect = "none"
        self.mode = "scanning"  # scanning | active | countdown | captured
        self.countdown_value = 0
        self.flash_intensity = 0
        self.captures_this_session = 0

        # ─── Systems ─────────────────────────────────
        self.camera = Camera()
        self.overlay = OverlayRenderer()
        self.logger = EventLogger()

        os.makedirs(PHOTO_SAVE_DIR, exist_ok=True)

        # ─── Window Setup ────────────────────────────
        self.setWindowTitle("SAY CHEESE!")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 750)
        self.setStyleSheet(STYLESHEET)

        self._build_ui()
        self._connect_signals()

        # ─── Timers ──────────────────────────────────
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._update_frame)
        self.frame_timer.start(1000 // CAMERA_FPS)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._countdown_tick)

        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._flash_decay)

        self.logger.log("APP_START")

    # ═══════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(20, 16, 20, 16)
        root_layout.setSpacing(12)

        # ─── Header ──────────────────────────────────
        header = self._build_header()
        root_layout.addLayout(header)

        # ─── Separator ───────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        root_layout.addWidget(sep)

        # ─── Main Content (Camera + Side Panel) ──────
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Camera area (left, takes most space)
        camera_area = self._build_camera_area()
        content_layout.addLayout(camera_area, stretch=7)

        # Side panel (right)
        side_panel = self._build_side_panel()
        content_layout.addWidget(side_panel, stretch=3)

        root_layout.addLayout(content_layout, stretch=1)

        # ─── Bottom Controls ─────────────────────────
        controls = self._build_controls()
        root_layout.addLayout(controls)

    def _build_header(self):
        layout = QHBoxLayout()

        # Left: title block
        title_block = QVBoxLayout()
        title_block.setSpacing(2)

        self.title_label = QLabel("SAY CHEESE!")
        self.title_label.setObjectName("title")
        title_block.addWidget(self.title_label)

        self.subtitle_label = QLabel("GESTURE-CONTROLLED CAMERA EXPERIENCE")
        self.subtitle_label.setObjectName("subtitle")
        title_block.addWidget(self.subtitle_label)

        layout.addLayout(title_block)
        layout.addStretch()

        # Right: status pill
        self.status_label = QLabel("● SCANNING")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        return layout

    def _build_camera_area(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        self.camera_label = QLabel()
        self.camera_label.setObjectName("cameraFeed")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setMinimumSize(480, 360)

        # Drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.camera_label.setGraphicsEffect(shadow)

        layout.addWidget(self.camera_label)

        # Effects bar
        effects_layout = QHBoxLayout()
        effects_layout.setSpacing(8)

        fx_label = QLabel("FX")
        fx_label.setObjectName("sectionTitle")
        effects_layout.addWidget(fx_label)

        self.effect_buttons = []
        for effect in EFFECTS:
            btn = QPushButton(effect["icon"])
            btn.setObjectName("effectBtnActive" if effect["key"] == self.current_effect else "effectBtn")
            btn.setToolTip(effect["name"])
            btn.setProperty("effect_key", effect["key"])
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, k=effect["key"]: self._set_effect(k))
            self.effect_buttons.append(btn)
            effects_layout.addWidget(btn)

        effects_layout.addStretch()
        layout.addLayout(effects_layout)

        return layout

    def _build_side_panel(self):
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(12)
        panel_layout.setContentsMargins(12, 12, 12, 12)

        # ─── Stats Row ───────────────────────────────
        stats_title = QLabel("SESSION")
        stats_title.setObjectName("sectionTitle")
        panel_layout.addWidget(stats_title)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        # Captures count
        captures_block = QVBoxLayout()
        captures_block.setSpacing(0)
        self.captures_count_label = QLabel("0")
        self.captures_count_label.setObjectName("statsLabel")
        self.captures_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        captures_block.addWidget(self.captures_count_label)
        cap_caption = QLabel("CAPTURES")
        cap_caption.setObjectName("statsCaption")
        cap_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        captures_block.addWidget(cap_caption)
        stats_row.addLayout(captures_block)

        # Events count
        events_block = QVBoxLayout()
        events_block.setSpacing(0)
        self.events_count_label = QLabel("0")
        self.events_count_label.setObjectName("statsLabel")
        self.events_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        events_block.addWidget(self.events_count_label)
        evt_caption = QLabel("EVENTS")
        evt_caption.setObjectName("statsCaption")
        evt_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        events_block.addWidget(evt_caption)
        stats_row.addLayout(events_block)

        panel_layout.addLayout(stats_row)

        # ─── Separator ───────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        panel_layout.addWidget(sep)

        # ─── Event Log ───────────────────────────────
        log_title = QLabel("EVENT LOG")
        log_title.setObjectName("sectionTitle")
        panel_layout.addWidget(log_title)

        self.log_labels = []
        for i in range(8):
            log_line = QLabel("—")
            log_line.setObjectName("eventLog")
            self.log_labels.append(log_line)
            panel_layout.addWidget(log_line)

        # ─── Separator ───────────────────────────────
        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.HLine)
        panel_layout.addWidget(sep2)

        # ─── Gallery ─────────────────────────────────
        gallery_title = QLabel("RECENT CAPTURES")
        gallery_title.setObjectName("sectionTitle")
        panel_layout.addWidget(gallery_title)

        self.gallery_layout = QGridLayout()
        self.gallery_layout.setSpacing(4)
        panel_layout.addLayout(self.gallery_layout)

        panel_layout.addStretch()

        return panel

    def _build_controls(self):
        layout = QHBoxLayout()
        layout.setSpacing(12)

        layout.addStretch()

        # Capture button
        self.capture_btn = QPushButton("◉  CAPTURE")
        self.capture_btn.setObjectName("captureBtn")
        self.capture_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.capture_btn)

        layout.addStretch()

        # Keyboard shortcut hint
        hint = QLabel("SPACE to capture  ·  1-6 effects  ·  ESC to quit")
        hint.setObjectName("subtitle")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch()

        return layout

    def _connect_signals(self):
        self.capture_btn.clicked.connect(self._start_capture)

    # ═══════════════════════════════════════════════════════════════
    #  FRAME UPDATE LOOP
    # ═══════════════════════════════════════════════════════════════

    def _update_frame(self):
        frame, face_data, motion_data = self.camera.get_frame()
        if frame is None:
            return

        # ─── State Transitions ────────────────────────
        if face_data:
            face_detected = face_data["count"] > 0

            if face_detected and not self.face_present:
                self.mode = "active"
                self._set_status("● FACE DETECTED", COLORS["accent_green"])
                self.logger.log("FACE_DETECTED")
                self.face_present = True

            elif not face_detected and self.face_present:
                self.mode = "scanning"
                self._set_status("● SCANNING", COLORS["text_dim"])
                self.logger.log("FACE_LOST")
                self.face_present = False

        if motion_data:
            motion_detected = motion_data["detected"]
            if motion_detected and not self.hands_present:
                self.logger.log("MOTION_DETECTED", motion_data.get("zone"))
                self.hands_present = True
            elif not motion_detected and self.hands_present:
                self.logger.log("MOTION_LOST")
                self.hands_present = False

        # ─── Apply Visual Effect ──────────────────────
        frame = apply_effect(frame, self.current_effect)

        # ─── Render Overlays ──────────────────────────
        state = {
            "mode": self.mode,
            "countdown": self.countdown_value,
            "flash": self.flash_intensity,
            "effect_name": self.current_effect,
        }
        frame = self.overlay.render(frame, face_data, motion_data, state)

        # ─── Display ─────────────────────────────────
        self._display_frame(frame)

        # ─── Update sidebar stats (throttled) ────────
        if self.camera.frame_count % 30 == 0:
            self._update_sidebar()

    def _display_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        scaled = pixmap.scaled(
            self.camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled)

    # ═══════════════════════════════════════════════════════════════
    #  CAPTURE SYSTEM
    # ═══════════════════════════════════════════════════════════════

    def _start_capture(self):
        if self.mode == "countdown":
            return  # already in progress

        self.mode = "countdown"
        self.countdown_value = COUNTDOWN_SECONDS
        self._set_status("● CAPTURING...", COLORS["accent_pink"])
        self.logger.log("CAPTURE_COUNTDOWN_START")
        self.countdown_timer.start(1000)

    def _countdown_tick(self):
        self.countdown_value -= 1
        if self.countdown_value <= 0:
            self.countdown_timer.stop()
            self._take_photo()

    def _take_photo(self):
        """Capture the actual photo."""
        frame = self.camera.capture_raw()
        if frame is None:
            return

        # Apply current effect to saved photo
        frame = apply_effect(frame, self.current_effect)

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        filepath = os.path.join(PHOTO_SAVE_DIR, filename)

        import cv2
        cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        self.logger.log_capture(filepath, self.current_effect, "manual")
        self.logger.log("PHOTO_CAPTURED", filepath)
        self.captures_this_session += 1

        # Flash effect
        self.flash_intensity = 1.0
        self.flash_timer.start(30)

        # Reset mode
        self.mode = "active" if self.face_present else "scanning"
        self._set_status("✓ CAPTURED!", COLORS["accent_cyan"])

        # Add to gallery
        self._add_gallery_thumb(frame, filepath)

        # Reset status after delay
        QTimer.singleShot(2000, self._reset_status)

    def _flash_decay(self):
        self.flash_intensity -= 0.08
        if self.flash_intensity <= 0:
            self.flash_intensity = 0
            self.flash_timer.stop()

    # ═══════════════════════════════════════════════════════════════
    #  EFFECTS
    # ═══════════════════════════════════════════════════════════════

    def _set_effect(self, key):
        self.current_effect = key
        self.logger.log("EFFECT_CHANGED", key)

        # Update button styles
        for btn in self.effect_buttons:
            if btn.property("effect_key") == key:
                btn.setObjectName("effectBtnActive")
            else:
                btn.setObjectName("effectBtn")
            btn.setStyle(btn.style())  # force style refresh

    # ═══════════════════════════════════════════════════════════════
    #  UI UPDATES
    # ═══════════════════════════════════════════════════════════════

    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color}; border-color: {color}; "
            f"background-color: {COLORS['bg_elevated']}; "
            f"font-size: 12px; font-weight: 500; "
            f"padding: 6px 14px; border: 1px solid; border-radius: 16px;"
        )

    def _reset_status(self):
        if self.face_present:
            self._set_status("● FACE DETECTED", COLORS["accent_green"])
        else:
            self._set_status("● SCANNING", COLORS["text_dim"])

    def _update_sidebar(self):
        stats = self.logger.get_stats()
        self.captures_count_label.setText(str(self.captures_this_session))
        self.events_count_label.setText(str(stats["total_events"]))

        # Update event log
        recent = self.logger.get_recent_events(8)
        for i, label in enumerate(self.log_labels):
            if i < len(recent):
                ts, evt, detail = recent[i]
                time_str = ts[11:19]  # HH:MM:SS
                detail_str = f" → {detail}" if detail else ""
                label.setText(f"{time_str}  {evt}{detail_str}")
            else:
                label.setText("—")

    def _add_gallery_thumb(self, frame, filepath):
        """Add a thumbnail to the gallery grid."""
        h, w = frame.shape[:2]
        thumb_size = 64

        # Create thumbnail
        qt_image = QImage(frame.data, w, h, w * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        thumb = pixmap.scaled(thumb_size, thumb_size,
                              Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                              Qt.TransformationMode.SmoothTransformation)

        label = QLabel()
        label.setObjectName("galleryThumb")
        label.setPixmap(thumb)
        label.setFixedSize(thumb_size, thumb_size)
        label.setScaledContents(True)

        # Add to grid (fill left to right, top to bottom)
        count = self.gallery_layout.count()
        row = count // 3
        col = count % 3
        if row < 3:  # max 3 rows of 3
            self.gallery_layout.addWidget(label, row, col)

    # ═══════════════════════════════════════════════════════════════
    #  KEYBOARD SHORTCUTS
    # ═══════════════════════════════════════════════════════════════

    def keyPressEvent(self, event):
        key = event.key()

        # Space = capture
        if key == Qt.Key.Key_Space:
            self._start_capture()

        # 1-6 = effects
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_6:
            idx = key - Qt.Key.Key_1
            if idx < len(EFFECTS):
                self._set_effect(EFFECTS[idx]["key"])

        # Escape = quit
        elif key == Qt.Key.Key_Escape:
            self.close()

        else:
            super().keyPressEvent(event)

    # ═══════════════════════════════════════════════════════════════
    #  CLEANUP
    # ═══════════════════════════════════════════════════════════════

    def closeEvent(self, event):
        self.frame_timer.stop()
        self.countdown_timer.stop()
        self.flash_timer.stop()
        self.camera.release()
        self.logger.log("APP_CLOSE")
        self.logger.close()
        event.accept()