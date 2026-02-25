"""
Say Cheese! — Main Window
RETRO ARCADE EDITION
Photo booth + live dashboard + neon pixel aesthetic.
"""

import os
import time
import math
from datetime import datetime
from collections import deque

from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QSizePolicy,
    QGridLayout, QTabWidget
)
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import (
    QImage, QPixmap, QColor, QFont, QPainter, QPen,
    QLinearGradient, QBrush, QPainterPath
)

from vision.camera import Camera
from vision.effects import apply_effect
from ui.overlays import OverlayRenderer
from data.database import EventLogger
from config import (
    COLORS, EFFECTS, BOOTH_FRAMES, COUNTDOWN_SECONDS,
    CAMERA_FPS, PHOTO_SAVE_DIR, GRAPH_HISTORY_SIZE, GRAPH_UPDATE_INTERVAL
)


# ═══════════════════════════════════════════════════════════════════
#  STYLESHEET — RETRO ARCADE
# ═══════════════════════════════════════════════════════════════════

STYLESHEET = f"""
    * {{
        font-family: 'Consolas', 'Courier New', monospace;
    }}

    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}

    QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
    }}

    QLabel#title {{
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 6px;
        color: {COLORS['neon_green']};
    }}

    QLabel#subtitle {{
        font-size: 10px;
        font-weight: 400;
        color: {COLORS['text_dim']};
        letter-spacing: 2px;
    }}

    QLabel#status {{
        font-size: 11px;
        font-weight: 700;
        color: {COLORS['neon_green']};
        padding: 4px 12px;
        border: 2px solid {COLORS['neon_green']};
        background-color: rgba(57, 255, 20, 0.05);
        letter-spacing: 1px;
    }}

    QLabel#cameraFeed {{
        border: 2px solid {COLORS['neon_green']};
        background-color: #000000;
    }}

    QPushButton {{
        border: 2px solid {COLORS['border']};
        padding: 6px 14px;
        font-size: 11px;
        font-weight: 700;
        color: {COLORS['text_primary']};
        background-color: {COLORS['bg_elevated']};
        letter-spacing: 1px;
        font-family: 'Consolas', 'Courier New', monospace;
    }}

    QPushButton:hover {{
        background-color: {COLORS['bg_card']};
        border-color: {COLORS['neon_cyan']};
        color: {COLORS['neon_cyan']};
    }}

    QPushButton:pressed {{
        background-color: {COLORS['bg_dark']};
    }}

    QPushButton#captureBtn {{
        font-size: 13px;
        padding: 10px 24px;
        border: 3px solid {COLORS['neon_pink']};
        color: {COLORS['neon_pink']};
        background-color: rgba(255, 45, 123, 0.08);
        letter-spacing: 3px;
    }}

    QPushButton#captureBtn:hover {{
        background-color: rgba(255, 45, 123, 0.2);
    }}

    QPushButton#effectBtn {{
        min-width: 36px;
        min-height: 36px;
        max-width: 36px;
        max-height: 36px;
        padding: 0;
        font-size: 14px;
        border: 2px solid {COLORS['border']};
    }}

    QPushButton#effectBtnActive {{
        min-width: 36px;
        min-height: 36px;
        max-width: 36px;
        max-height: 36px;
        padding: 0;
        font-size: 14px;
        border: 2px solid {COLORS['neon_cyan']};
        background-color: rgba(0, 255, 247, 0.15);
        color: {COLORS['neon_cyan']};
    }}

    QPushButton#frameBtn {{
        min-width: 32px;
        min-height: 32px;
        max-width: 32px;
        max-height: 32px;
        padding: 0;
        font-size: 13px;
        border: 2px solid {COLORS['border']};
    }}

    QPushButton#frameBtnActive {{
        min-width: 32px;
        min-height: 32px;
        max-width: 32px;
        max-height: 32px;
        padding: 0;
        font-size: 13px;
        border: 2px solid {COLORS['neon_pink']};
        background-color: rgba(255, 45, 123, 0.15);
        color: {COLORS['neon_pink']};
    }}

    QFrame#separator {{
        background-color: {COLORS['border']};
        max-height: 1px;
    }}

    QFrame#sidePanel {{
        background-color: {COLORS['bg_card']};
        border: 2px solid {COLORS['border']};
        padding: 8px;
    }}

    QLabel#sectionTitle {{
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 3px;
        color: {COLORS['neon_cyan']};
    }}

    QLabel#eventLog {{
        font-size: 9px;
        color: {COLORS['text_muted']};
        font-family: 'Consolas', 'Courier New', monospace;
    }}

    QLabel#scoreLabel {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS['neon_yellow']};
        letter-spacing: 2px;
    }}

    QLabel#scoreCaption {{
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 3px;
        color: {COLORS['text_dim']};
    }}

    QLabel#statValue {{
        font-size: 16px;
        font-weight: 700;
        color: {COLORS['neon_green']};
    }}

    QLabel#statCaption {{
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 2px;
        color: {COLORS['text_dim']};
    }}

    QLabel#galleryThumb {{
        border: 2px solid {COLORS['border']};
        background-color: {COLORS['bg_dark']};
    }}

    QTabWidget::pane {{
        border: 2px solid {COLORS['border']};
        background-color: {COLORS['bg_card']};
    }}

    QTabBar::tab {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_dim']};
        border: 2px solid {COLORS['border']};
        border-bottom: none;
        padding: 5px 12px;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
        font-family: 'Consolas', 'Courier New', monospace;
    }}

    QTabBar::tab:selected {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['neon_cyan']};
        border-color: {COLORS['neon_cyan']};
    }}
"""


# ═══════════════════════════════════════════════════════════════════
#  LIVE GRAPH WIDGET
# ═══════════════════════════════════════════════════════════════════

class RetroGraphWidget(QWidget):
    """A retro-styled live graph that looks like an arcade monitor."""

    def __init__(self, title="", color="#39ff14", max_value=10, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = QColor(color)
        self.max_value = max_value
        self.data = deque([0] * GRAPH_HISTORY_SIZE, maxlen=GRAPH_HISTORY_SIZE)
        self.setMinimumHeight(70)
        self.setMaximumHeight(90)

    def add_point(self, value):
        self.data.append(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # pixel-sharp!

        w = self.width()
        h = self.height()
        margin_top = 14
        margin_bottom = 4
        graph_h = h - margin_top - margin_bottom

        # Background
        painter.fillRect(0, 0, w, h, QColor(COLORS["bg_dark"]))

        # Border
        pen = QPen(QColor(COLORS["border"]))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, margin_top, w - 1, graph_h)

        # Title
        painter.setPen(QColor(COLORS["neon_cyan"]))
        font = QFont("Consolas", 7)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(2, 10, self.title)

        # Current value
        if self.data:
            val_text = str(int(self.data[-1]))
            painter.setPen(self.color)
            fm = painter.fontMetrics()
            painter.drawText(w - fm.horizontalAdvance(val_text) - 4, 10, val_text)

        # Grid lines (horizontal)
        painter.setPen(QPen(QColor(COLORS["border"]), 1))
        for i in range(1, 4):
            y = margin_top + int(graph_h * i / 4)
            # Dotted line
            for x in range(0, w, 6):
                painter.drawPoint(x, y)

        # Data line
        if len(self.data) < 2:
            return

        pen = QPen(self.color, 2)
        painter.setPen(pen)

        points = list(self.data)
        max_val = max(self.max_value, max(points) + 1)
        step_x = w / (len(points) - 1) if len(points) > 1 else 1

        for i in range(1, len(points)):
            x1 = int((i - 1) * step_x)
            x2 = int(i * step_x)
            y1 = margin_top + graph_h - int((points[i - 1] / max_val) * graph_h)
            y2 = margin_top + graph_h - int((points[i] / max_val) * graph_h)

            # Clamp
            y1 = max(margin_top, min(y1, margin_top + graph_h))
            y2 = max(margin_top, min(y2, margin_top + graph_h))

            painter.drawLine(x1, y1, x2, y2)

        # Glow effect: draw again with lighter color, slightly offset
        glow_color = QColor(self.color)
        glow_color.setAlpha(60)
        pen = QPen(glow_color, 4)
        painter.setPen(pen)

        for i in range(1, len(points)):
            x1 = int((i - 1) * step_x)
            x2 = int(i * step_x)
            y1 = margin_top + graph_h - int((points[i - 1] / max_val) * graph_h)
            y2 = margin_top + graph_h - int((points[i] / max_val) * graph_h)
            y1 = max(margin_top, min(y1, margin_top + graph_h))
            y2 = max(margin_top, min(y2, margin_top + graph_h))
            painter.drawLine(x1, y1, x2, y2)

        painter.end()


# ═══════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ─── Core State ──────────────────────────────
        self.face_present = False
        self.hands_present = False
        self.current_effect = "none"
        self.current_frame = "none"
        self.mode = "scanning"
        self.countdown_value = 0
        self.flash_intensity = 0
        self.captures_this_session = 0

        # Score system — earn points for interactions!
        self.score = 0
        self.combo = 0
        self.last_event_time = 0

        # Dashboard data
        self.face_history = deque([0] * GRAPH_HISTORY_SIZE, maxlen=GRAPH_HISTORY_SIZE)
        self.motion_history = deque([0] * GRAPH_HISTORY_SIZE, maxlen=GRAPH_HISTORY_SIZE)
        self.events_per_second = 0
        self.events_this_tick = 0

        # ─── Systems ─────────────────────────────────
        self.camera = Camera()
        self.overlay = OverlayRenderer()
        self.logger = EventLogger()

        os.makedirs(PHOTO_SAVE_DIR, exist_ok=True)

        # ─── Window Setup ────────────────────────────
        self.setWindowTitle("SAY CHEESE! — ARCADE MODE")
        self.setMinimumSize(1200, 740)
        self.resize(1300, 780)
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

        # Dashboard graph update timer (1 per second)
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self._update_graphs)
        self.graph_timer.start(GRAPH_UPDATE_INTERVAL)

        self.logger.log("APP_START")
        self._add_score(100, "GAME START")

    # ═══════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        # ─── Header ──────────────────────────────────
        header = self._build_header()
        root.addLayout(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        root.addWidget(sep)

        # ─── Main Content ────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(12)

        # Camera + controls (left)
        camera_col = self._build_camera_column()
        content.addLayout(camera_col, stretch=6)

        # Side panel with tabs (right)
        side = self._build_side_panel()
        content.addWidget(side, stretch=4)

        root.addLayout(content, stretch=1)

        # ─── Bottom Bar ──────────────────────────────
        bottom = self._build_bottom_bar()
        root.addLayout(bottom)

    def _build_header(self):
        layout = QHBoxLayout()

        # Title with neon glow effect
        title_block = QVBoxLayout()
        title_block.setSpacing(0)

        title = QLabel("SAY CHEESE!")
        title.setObjectName("title")
        title_block.addWidget(title)

        subtitle = QLabel(">>> ARCADE MODE <<<")
        subtitle.setObjectName("subtitle")
        title_block.addWidget(subtitle)

        layout.addLayout(title_block)
        layout.addStretch()

        # Score display
        score_block = QVBoxLayout()
        score_block.setSpacing(0)
        score_block.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.score_label = QLabel("000000")
        self.score_label.setObjectName("scoreLabel")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        score_block.addWidget(self.score_label)

        score_caption = QLabel("HIGH SCORE")
        score_caption.setObjectName("scoreCaption")
        score_caption.setAlignment(Qt.AlignmentFlag.AlignRight)
        score_block.addWidget(score_caption)

        layout.addLayout(score_block)

        # Spacer
        layout.addSpacing(20)

        # Status
        self.status_label = QLabel(">> SCANNING <<")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        return layout

    def _build_camera_column(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Camera feed
        self.camera_label = QLabel()
        self.camera_label.setObjectName("cameraFeed")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setMinimumSize(480, 360)

        # Neon glow shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(57, 255, 20, 50))
        shadow.setOffset(0, 0)
        self.camera_label.setGraphicsEffect(shadow)

        layout.addWidget(self.camera_label)

        # ─── Effects Row ─────────────────────────────
        fx_row = QHBoxLayout()
        fx_row.setSpacing(6)

        fx_label = QLabel("FX")
        fx_label.setObjectName("sectionTitle")
        fx_row.addWidget(fx_label)

        self.effect_buttons = []
        for effect in EFFECTS:
            btn = QPushButton(effect["icon"])
            active = effect["key"] == self.current_effect
            btn.setObjectName("effectBtnActive" if active else "effectBtn")
            btn.setToolTip(effect["name"])
            btn.setProperty("effect_key", effect["key"])
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=effect["key"]: self._set_effect(k))
            self.effect_buttons.append(btn)
            fx_row.addWidget(btn)

        fx_row.addStretch()
        layout.addLayout(fx_row)

        # ─── Photo Booth Frames Row ──────────────────
        frame_row = QHBoxLayout()
        frame_row.setSpacing(6)

        frame_label = QLabel("FRAMES")
        frame_label.setObjectName("sectionTitle")
        frame_row.addWidget(frame_label)

        self.frame_buttons = []
        for bf in BOOTH_FRAMES:
            btn = QPushButton(bf["icon"])
            active = bf["key"] == self.current_frame
            btn.setObjectName("frameBtnActive" if active else "frameBtn")
            btn.setToolTip(bf["name"])
            btn.setProperty("frame_key", bf["key"])
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=bf["key"]: self._set_frame(k))
            self.frame_buttons.append(btn)
            frame_row.addWidget(btn)

        frame_row.addStretch()
        layout.addLayout(frame_row)

        return layout

    def _build_side_panel(self):
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(8)

        # Tabs: DASHBOARD | LOG | GALLERY
        self.tabs = QTabWidget()

        # ─── DASHBOARD TAB ───────────────────────────
        dashboard = QWidget()
        dash_layout = QVBoxLayout(dashboard)
        dash_layout.setContentsMargins(6, 6, 6, 6)
        dash_layout.setSpacing(8)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.stat_captures = self._make_stat_widget("0", "CAPTURES", COLORS["neon_pink"])
        stats_row.addLayout(self.stat_captures["layout"])

        self.stat_events = self._make_stat_widget("0", "EVENTS", COLORS["neon_cyan"])
        stats_row.addLayout(self.stat_events["layout"])

        self.stat_combo = self._make_stat_widget("x0", "COMBO", COLORS["neon_yellow"])
        stats_row.addLayout(self.stat_combo["layout"])

        dash_layout.addLayout(stats_row)

        # Graphs
        self.face_graph = RetroGraphWidget(
            title="FACE DETECTION",
            color=COLORS["neon_green"],
            max_value=3
        )
        dash_layout.addWidget(self.face_graph)

        self.motion_graph = RetroGraphWidget(
            title="MOTION ACTIVITY",
            color=COLORS["neon_cyan"],
            max_value=5
        )
        dash_layout.addWidget(self.motion_graph)

        self.events_graph = RetroGraphWidget(
            title="EVENTS / SEC",
            color=COLORS["neon_pink"],
            max_value=5
        )
        dash_layout.addWidget(self.events_graph)

        dash_layout.addStretch()
        self.tabs.addTab(dashboard, "DASHBOARD")

        # ─── LOG TAB ─────────────────────────────────
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(6, 6, 6, 6)
        log_layout.setSpacing(3)

        self.log_labels = []
        for i in range(16):
            log_line = QLabel("—")
            log_line.setObjectName("eventLog")
            self.log_labels.append(log_line)
            log_layout.addWidget(log_line)

        log_layout.addStretch()
        self.tabs.addTab(log_tab, "EVENT LOG")

        # ─── GALLERY TAB ─────────────────────────────
        gallery_tab = QWidget()
        gallery_layout = QVBoxLayout(gallery_tab)
        gallery_layout.setContentsMargins(6, 6, 6, 6)

        self.gallery_grid = QGridLayout()
        self.gallery_grid.setSpacing(4)
        gallery_layout.addLayout(self.gallery_grid)
        gallery_layout.addStretch()
        self.tabs.addTab(gallery_tab, "GALLERY")

        panel_layout.addWidget(self.tabs)

        return panel

    def _make_stat_widget(self, value, caption, color):
        """Create a stat display block."""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_label = QLabel(value)
        val_label.setObjectName("statValue")
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700;")
        layout.addWidget(val_label)

        cap_label = QLabel(caption)
        cap_label.setObjectName("statCaption")
        cap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cap_label)

        return {"layout": layout, "value": val_label, "caption": cap_label}

    def _build_bottom_bar(self):
        layout = QHBoxLayout()
        layout.setSpacing(12)

        layout.addStretch()

        # Capture button
        self.capture_btn = QPushButton(">> CAPTURE <<")
        self.capture_btn.setObjectName("captureBtn")
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.capture_btn)

        layout.addStretch()

        hint = QLabel("[SPACE] CAPTURE  [1-8] FX  [Q-T] FRAMES  [ESC] QUIT")
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
                self._set_status(">> FACE LOCKED <<", COLORS["neon_green"])
                self.logger.log("FACE_DETECTED")
                self._add_score(50, "FACE FOUND")
                self.face_present = True
                self.events_this_tick += 1

            elif not face_detected and self.face_present:
                self.mode = "scanning"
                self._set_status(">> SCANNING <<", COLORS["text_dim"])
                self.logger.log("FACE_LOST")
                self.face_present = False
                self.combo = 0
                self.events_this_tick += 1

            # Track face count for graph
            self.face_history.append(face_data["count"])

        if motion_data:
            motion_detected = motion_data["detected"]
            motion_count = len(motion_data.get("regions", []))
            self.motion_history.append(motion_count)

            if motion_detected and not self.hands_present:
                self.logger.log("MOTION_DETECTED", motion_data.get("zone"))
                self._add_score(10, "MOTION")
                self.hands_present = True
                self.events_this_tick += 1
            elif not motion_detected and self.hands_present:
                self.logger.log("MOTION_LOST")
                self.hands_present = False
                self.events_this_tick += 1
        else:
            self.motion_history.append(0)

        # ─── Apply Visual Effect ──────────────────────
        frame = apply_effect(frame, self.current_effect)

        # ─── Render Overlays ──────────────────────────
        state = {
            "mode": self.mode,
            "countdown": self.countdown_value,
            "flash": self.flash_intensity,
            "effect_name": self.current_effect,
            "booth_frame": self.current_frame,
            "score": self.score,
        }
        frame = self.overlay.render(frame, face_data, motion_data, state)

        # ─── Display ─────────────────────────────────
        self._display_frame(frame)

        # ─── Update sidebar (throttled) ──────────────
        if self.camera.frame_count % 15 == 0:
            self._update_sidebar()

    def _display_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(
            self.camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation  # pixel-sharp, no smoothing!
        )
        self.camera_label.setPixmap(scaled)

    # ═══════════════════════════════════════════════════════════════
    #  CAPTURE
    # ═══════════════════════════════════════════════════════════════

    def _start_capture(self):
        if self.mode == "countdown":
            return

        self.mode = "countdown"
        self.countdown_value = COUNTDOWN_SECONDS
        self._set_status(">> CHEESE!! <<", COLORS["neon_pink"])
        self.logger.log("CAPTURE_START")
        self.countdown_timer.start(1000)

    def _countdown_tick(self):
        self.countdown_value -= 1
        if self.countdown_value <= 0:
            self.countdown_timer.stop()
            self._take_photo()

    def _take_photo(self):
        frame = self.camera.capture_raw()
        if frame is None:
            return

        frame = apply_effect(frame, self.current_effect)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        filepath = os.path.join(PHOTO_SAVE_DIR, filename)

        import cv2
        cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        self.logger.log_capture(filepath, self.current_effect, "manual")
        self.logger.log("PHOTO_CAPTURED", filepath)
        self.captures_this_session += 1

        self._add_score(200, "PHOTO!")

        # Flash
        self.flash_intensity = 1.0
        self.flash_timer.start(30)

        self.mode = "active" if self.face_present else "scanning"
        self._set_status(">> CAPTURED! <<", COLORS["neon_yellow"])

        self._add_gallery_thumb(frame, filepath)
        self.events_this_tick += 1

        QTimer.singleShot(2000, self._reset_status)

    def _flash_decay(self):
        self.flash_intensity -= 0.08
        if self.flash_intensity <= 0:
            self.flash_intensity = 0
            self.flash_timer.stop()

    # ═══════════════════════════════════════════════════════════════
    #  EFFECTS & FRAMES
    # ═══════════════════════════════════════════════════════════════

    def _set_effect(self, key):
        self.current_effect = key
        self.logger.log("EFFECT_CHANGED", key)
        self._add_score(5, "FX SWITCH")

        for btn in self.effect_buttons:
            active = btn.property("effect_key") == key
            btn.setObjectName("effectBtnActive" if active else "effectBtn")
            btn.setStyle(btn.style())

    def _set_frame(self, key):
        self.current_frame = key
        self.logger.log("FRAME_CHANGED", key)
        self._add_score(5, "FRAME SWITCH")

        for btn in self.frame_buttons:
            active = btn.property("frame_key") == key
            btn.setObjectName("frameBtnActive" if active else "frameBtn")
            btn.setStyle(btn.style())

    # ═══════════════════════════════════════════════════════════════
    #  SCORE SYSTEM
    # ═══════════════════════════════════════════════════════════════

    def _add_score(self, points, reason=""):
        now = time.time()

        # Combo multiplier: quick successive actions boost score
        if now - self.last_event_time < 3.0:
            self.combo = min(self.combo + 1, 10)
        else:
            self.combo = 0

        multiplier = 1 + (self.combo * 0.2)
        earned = int(points * multiplier)
        self.score += earned
        self.last_event_time = now

        self.score_label.setText(f"{self.score:06d}")
        self.stat_combo["value"].setText(f"x{self.combo}")

    # ═══════════════════════════════════════════════════════════════
    #  DASHBOARD & SIDEBAR
    # ═══════════════════════════════════════════════════════════════

    def _update_graphs(self):
        """Called once per second to update dashboard graphs."""
        # Face graph
        recent_face = list(self.face_history)[-1] if self.face_history else 0
        self.face_graph.add_point(recent_face)

        # Motion graph
        recent_motion = list(self.motion_history)[-1] if self.motion_history else 0
        self.motion_graph.add_point(recent_motion)

        # Events per second graph
        self.events_graph.add_point(self.events_this_tick)
        self.events_per_second = self.events_this_tick
        self.events_this_tick = 0

    def _update_sidebar(self):
        stats = self.logger.get_stats()
        self.stat_captures["value"].setText(str(self.captures_this_session))
        self.stat_events["value"].setText(str(stats["total_events"]))

        # Event log
        recent = self.logger.get_recent_events(16)
        for i, label in enumerate(self.log_labels):
            if i < len(recent):
                ts, evt, detail = recent[i]
                time_str = ts[11:19]
                detail_str = f" > {detail}" if detail else ""
                label.setText(f"{time_str} {evt}{detail_str}")
                # Color code events
                if "CAPTURE" in evt:
                    label.setStyleSheet(f"color: {COLORS['neon_pink']};")
                elif "FACE" in evt:
                    label.setStyleSheet(f"color: {COLORS['neon_green']};")
                elif "MOTION" in evt:
                    label.setStyleSheet(f"color: {COLORS['neon_cyan']};")
                else:
                    label.setStyleSheet(f"color: {COLORS['text_muted']};")
            else:
                label.setText("—")

    def _add_gallery_thumb(self, frame, filepath):
        h, w = frame.shape[:2]
        thumb_size = 64

        qt_image = QImage(frame.data, w, h, w * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        thumb = pixmap.scaled(thumb_size, thumb_size,
                              Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                              Qt.TransformationMode.FastTransformation)

        label = QLabel()
        label.setObjectName("galleryThumb")
        label.setPixmap(thumb)
        label.setFixedSize(thumb_size, thumb_size)
        label.setScaledContents(True)

        count = self.gallery_grid.count()
        row = count // 4
        col = count % 4
        if row < 4:
            self.gallery_grid.addWidget(label, row, col)

    # ═══════════════════════════════════════════════════════════════
    #  UI HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color}; border-color: {color}; "
            f"background-color: {COLORS['bg_elevated']}; "
            f"font-size: 11px; font-weight: 700; "
            f"padding: 4px 12px; border: 2px solid; letter-spacing: 1px;"
        )

    def _reset_status(self):
        if self.face_present:
            self._set_status(">> FACE LOCKED <<", COLORS["neon_green"])
        else:
            self._set_status(">> SCANNING <<", COLORS["text_dim"])

    # ═══════════════════════════════════════════════════════════════
    #  KEYBOARD SHORTCUTS
    # ═══════════════════════════════════════════════════════════════

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Space:
            self._start_capture()
        elif 49 <= key <= 56:
            idx = key - 49
            if idx < len(EFFECTS):
                self._set_effect(EFFECTS[idx]["key"])
        # Q, W, E, R, T, Y for frames
        elif key == Qt.Key.Key_Q and len(BOOTH_FRAMES) > 0:
            self._set_frame(BOOTH_FRAMES[0]["key"])
        elif key == Qt.Key.Key_W and len(BOOTH_FRAMES) > 1:
            self._set_frame(BOOTH_FRAMES[1]["key"])
        elif key == Qt.Key.Key_E and len(BOOTH_FRAMES) > 2:
            self._set_frame(BOOTH_FRAMES[2]["key"])
        elif key == Qt.Key.Key_R and len(BOOTH_FRAMES) > 3:
            self._set_frame(BOOTH_FRAMES[3]["key"])
        elif key == Qt.Key.Key_T and len(BOOTH_FRAMES) > 4:
            self._set_frame(BOOTH_FRAMES[4]["key"])
        elif key == Qt.Key.Key_Y and len(BOOTH_FRAMES) > 5:
            self._set_frame(BOOTH_FRAMES[5]["key"])
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
        self.graph_timer.stop()
        self.camera.release()
        self.logger.log("APP_CLOSE")
        self.logger.close()
        event.accept()