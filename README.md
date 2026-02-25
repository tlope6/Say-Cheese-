# SAY CHEESE! 🕹️

### >>> ARCADE MODE <<<

A gesture-controlled desktop camera experience built with Python, PyQt5, and OpenCV. Interact with a live camera feed using hand movements and facial expressions — capture photos, switch visual effects, apply photo booth frames, and watch your activity on a live retro dashboard.

## Features

- **Live Camera Feed** with pixel-art HUD overlays (chunky neon brackets, arcade borders, retro scanlines)
- **8 Visual Effects**: None, Noir, Thermal, Glitch, Pixel, Vaporwave, CRT, Neon Edge
- **6 Photo Booth Frames**: Hearts, Stars, Arcade, Glitch, Rainbow (animated!)
- **Photo Capture** with big neon countdown and flash
- **Score System** — earn points for interactions, build combos with quick actions
- **Live Dashboard** with real-time graphs (face detection, motion activity, events/sec)
- **Color-coded Event Log** tracking every interaction
- **Photo Gallery** tab with capture thumbnails
- **Motion Detection** with zone-based tracking
- **Face Detection** with stability analysis
- **Event Logging** — every interaction saved to SQLite

## Setup

```bash
cd say-cheese

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

pip install -r requirements.txt

# Delete old database if upgrading
# del data\events.db

python main.py
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Start capture countdown |
| `1-8` | Switch visual effects |
| `Q-Y` | Switch photo booth frames |
| `Esc` | Quit |

## Project Structure

```
say_cheese/
├── main.py              # Entry point
├── config.py            # Settings, colors, effects, frames
├── requirements.txt
├── vision/
│   ├── camera.py        # Camera capture pipeline
│   ├── face.py          # Haar cascade face detection
│   ├── hands.py         # Motion-based tracking
│   └── effects.py       # Visual effects (8 total)
├── ui/
│   ├── main_window.py   # Main app window + dashboard + gallery
│   └── overlays.py      # Retro HUD + photo booth frames
├── data/
│   └── database.py      # SQLite event logger
├── audio/               # Sound effects (future)
├── assets/              # Images, sounds
└── captures/            # Saved photos
```

## Next Steps

- [ ] MediaPipe integration for real hand gesture recognition
- [ ] Specific gestures: peace sign → capture, thumbs up → effect cycle
- [ ] Sound effects (8-bit shutter click, coin sounds for scoring)
- [ ] Gesture-based UI navigation
- [ ] Leaderboard / high score persistence
- [ ] Export photos with metadata and frames baked in

---

*Exploring the intersection of human-computer interaction, creative coding, and machine perception — now with extra pixels.*