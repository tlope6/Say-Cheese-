# SAY CHEESE! 📸

A gesture-controlled desktop camera experience built with Python, PyQt5, and OpenCV. Interact with a live camera feed using hand movements and facial expressions — capture photos, switch visual effects, and watch every interaction logged in real time.

## Features

- **Live Camera Feed** with HUD-style overlays (face brackets, scan lines, crosshairs)
- **6 Visual Effects**: None, Noir, Thermal, Glitch, Pixel, Vaporwave
- **Photo Capture** with countdown timer and flash animation
- **Motion Detection** with zone-based tracking
- **Face Detection** with stability analysis
- **Event Logging** — every interaction saved to SQLite
- **Live Stats** sidebar with event log and capture gallery
- **Keyboard Shortcuts**: `Space` capture, `1-6` effects, `Esc` quit

## Setup

```bash
# Clone and enter the project
cd say-cheese

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Project Structure

```
say_cheese/
├── main.py              # Entry point
├── config.py            # All settings & constants
├── requirements.txt
├── vision/
│   ├── camera.py        # Camera capture + pipeline
│   ├── face.py          # Haar cascade face detection
│   ├── hands.py         # Motion-based tracking
│   └── effects.py       # Visual effects (noir, thermal, etc.)
├── ui/
│   ├── main_window.py   # Main application window
│   └── overlays.py      # HUD overlay renderer
├── data/
│   └── database.py      # SQLite event logger
├── audio/               # Sound effects (future)
├── assets/              # Images, sounds
└── captures/            # Saved photos
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Start capture countdown |
| `1` | No effect |
| `2` | Noir |
| `3` | Thermal |
| `4` | Glitch |
| `5` | Pixel |
| `6` | Vaporwave |
| `Esc` | Quit |

## Next Steps

- [ ] MediaPipe integration for real hand gesture recognition
- [ ] Specific gestures: peace sign → capture, thumbs up → effect cycle
- [ ] Sound effects (shutter click, mode switch)
- [ ] Photo gallery browser view
- [ ] Gesture-based UI navigation (wave to scroll effects)
- [ ] Export photos with metadata

---

*Exploring the intersection of human-computer interaction, creative coding, and machine perception.*