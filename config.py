"""
Say Cheese! — Global Configuration
RETRO ARCADE EDITION
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
GESTURE_COOLDOWN_MS = 1500
GESTURE_CONFIRM_FRAMES = 5
MOTION_AREA_THRESHOLD = 3000

# ─── Photo Capture ────────────────────────────────────────────────
COUNTDOWN_SECONDS = 3
PHOTO_SAVE_DIR = "captures"

# ─── UI Theme — RETRO ARCADE / NEON ──────────────────────────────
COLORS = {
    # Backgrounds
    "bg_dark":       "#0d0d1a",
    "bg_card":       "#12122a",
    "bg_elevated":   "#1a1a3e",
    "bg_input":      "#0a0a18",

    # Borders
    "border":        "#2a2a5a",
    "border_glow":   "#3a3a7a",

    # Text
    "text_primary":  "#e0e0ff",
    "text_dim":      "#6666aa",
    "text_muted":    "#444488",

    # Neon accents
    "neon_green":    "#39ff14",
    "neon_pink":     "#ff2d7b",
    "neon_cyan":     "#00fff7",
    "neon_yellow":   "#ffe600",
    "neon_orange":   "#ff6b1a",
    "neon_purple":   "#bf5fff",
    "neon_blue":     "#4d4dff",

    # Functional
    "accent_green":  "#39ff14",
    "accent_pink":   "#ff2d7b",
    "accent_cyan":   "#00fff7",
    "accent_amber":  "#ffe600",
    "accent_purple": "#bf5fff",
}

# ─── Pixel Font Families (fallback chain) ────────────────────────
FONT_PIXEL = "'Press Start 2P', 'Courier New', 'Consolas', monospace"
FONT_BODY = "'VT323', 'Courier New', 'Consolas', monospace"

# ─── Effects ──────────────────────────────────────────────────────
EFFECTS = [
    {"name": "None",       "key": "none",       "icon": "▪"},
    {"name": "Noir",       "key": "noir",       "icon": "◈"},
    {"name": "Thermal",    "key": "thermal",    "icon": "◆"},
    {"name": "Glitch",     "key": "glitch",     "icon": "⚡"},
    {"name": "Pixel",      "key": "pixel",      "icon": "▦"},
    {"name": "Vaporwave",  "key": "vaporwave",  "icon": "◇"},
    {"name": "CRT",        "key": "crt",        "icon": "▣"},
    {"name": "Neon Edge",  "key": "neon_edge",  "icon": "◎"},
]

# ─── Photo Booth Frames ──────────────────────────────────────────
BOOTH_FRAMES = [
    {"name": "None",        "key": "none",       "icon": "—"},
    {"name": "Pixel Heart", "key": "hearts",     "icon": "♥"},
    {"name": "Stars",       "key": "stars",      "icon": "★"},
    {"name": "Arcade",      "key": "arcade",     "icon": "◈"},
    {"name": "Glitch",      "key": "glitch_frame","icon": "⚡"},
    {"name": "Rainbow",     "key": "rainbow",    "icon": "≈"},
]

# ─── Dashboard ────────────────────────────────────────────────────
GRAPH_HISTORY_SIZE = 60  # data points to keep (1 per second)
GRAPH_UPDATE_INTERVAL = 1000  # ms between graph updates