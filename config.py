"""
Say Cheese! — Global Configuration
"""

# ─── Camera ───────────────────────────────────────────────────────
CAMERA_INDEX = 0
CAMERA_FPS = 30
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ─── Face Detection ───────────────────────────────────────────────
FACE_SCALE_FACTOR = 1.2
FACE_MIN_NEIGHBORS = 5
FACE_MIN_SIZE = (80, 80)

# ─── Gesture Thresholds ──────────────────────────────────────────
GESTURE_COOLDOWN_MS = 1500       # ms between gesture triggers
GESTURE_CONFIRM_FRAMES = 5      # frames a gesture must be held
MOTION_AREA_THRESHOLD = 3000    # min contour area for motion

# ─── Photo Capture ────────────────────────────────────────────────
COUNTDOWN_SECONDS = 3
PHOTO_SAVE_DIR = "captures"

# ─── UI Theme ─────────────────────────────────────────────────────
COLORS = {
    "bg_dark":       "#0a0a0a",
    "bg_card":       "#111111",
    "bg_elevated":   "#1a1a1a",
    "border":        "#222222",
    "border_glow":   "#2a2a2a",
    "text_primary":  "#f0f0f0",
    "text_dim":      "#666666",
    "text_muted":    "#444444",
    "accent_green":  "#00ff88",
    "accent_cyan":   "#00e5ff",
    "accent_pink":   "#ff3366",
    "accent_amber":  "#ffaa00",
    "accent_purple": "#aa55ff",
    "scan_line":     "#00ff8844",
    "overlay_dark":  "rgba(0, 0, 0, 0.7)",
}

# ─── Effects ──────────────────────────────────────────────────────
EFFECTS = [
    {"name": "None",       "key": "none",       "icon": "✦"},
    {"name": "Noir",       "key": "noir",       "icon": "🎬"},
    {"name": "Thermal",    "key": "thermal",    "icon": "🔥"},
    {"name": "Glitch",     "key": "glitch",     "icon": "⚡"},
    {"name": "Pixel",      "key": "pixel",      "icon": "▦"},
    {"name": "Vaporwave",  "key": "vaporwave",  "icon": "🌊"},
]