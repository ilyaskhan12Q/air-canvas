<div align="center">

# ✋ Air Canvas

### Real-time Hand Gesture Drawing — Powered by MediaPipe & OpenCV

[![CI](https://github.com/your-username/air-canvas/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/air-canvas/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9+-0097A7?logo=google&logoColor=white)](https://mediapipe.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

<br/>

**Draw glowing neon trails in the air with just your index finger.**  
No stylus. No touchscreen. Just your hand and a webcam.

<br/>

<!-- Replace with an actual demo GIF after recording -->
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ✌️  Point → Draw     ✊  Fist → Pause               ║
║        🖐️  Palm → Erase    👍  Thumb → Clear               ║
║                                                              ║
║     [ Neon Glow · Rainbow · Sparkle · Pastel · Classic ]    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

[**Live Demo**](#) · [**Report Bug**](.github/ISSUE_TEMPLATE/bug_report.md) · [**Request Feature**](.github/ISSUE_TEMPLATE/feature_request.md) · [**Contribute**](CONTRIBUTING.md)

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🖥️ Demo](#️-demo)
- [⚙️ How It Works](#️-how-it-works)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
- [✌️ Gesture Reference](#️-gesture-reference)
- [🎨 Effect Modes](#-effect-modes)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🧪 Testing](#-testing)
- [🐳 Docker](#-docker)
- [🛣️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [🔒 Security](#-security)
- [📄 License](#-license)
- [🙏 Acknowledgements](#-acknowledgements)

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🤚 **Real-time hand tracking** | MediaPipe Hands — 21 landmarks at 30+ FPS |
| ✌️ **4 gesture commands** | Draw, Pause, Erase, Clear — purely geometric, no ML model needed |
| 🌈 **5 visual effects** | Neon Glow, Rainbow, Sparkle, Pastel, Classic |
| ✨ **Particle system** | Physics-simulated glowing particles trail your brush |
| 🦴 **Skeleton overlay** | Neon-coloured hand wireframe (toggleable) |
| 🖌️ **8 brush colours + custom** | Full colour picker + palette shortcuts |
| 📊 **Live stats HUD** | FPS counter, stroke count, active effect |
| 📸 **Screenshot export** | Save your artwork to disk |
| 🖥️ **Streamlit UI** | Browser-based, works on any OS with a webcam |
| ✅ **Tested** | pytest + GitHub Actions CI (3 OS × 4 Python versions) |

---

## 🖥️ Demo

> **To add your own demo GIF:**
> 1. Record a 10–15 second clip of the app running
> 2. Convert to GIF with [Gifski](https://gif.ski/) or [ffmpeg](https://ffmpeg.org/)
> 3. Save as `assets/demo.gif` and replace the placeholder below

```
[Demo GIF — replace with assets/demo.gif]
```

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Air Canvas Pipeline                     │
│                                                             │
│  Webcam Frame                                               │
│       │                                                     │
│       ▼                                                     │
│  HandTracker (MediaPipe)                                    │
│  ├─ 21 landmark points (x, y, z)                           │
│  └─ Skeleton annotation frame                               │
│       │                                                     │
│       ▼                                                     │
│  GestureRecognizer                                          │
│  ├─ Finger-state geometry rules                             │
│  └─ Output: DRAW | PAUSE | ERASE | CLEAR | UNKNOWN         │
│       │                                                     │
│       ▼                                                     │
│  AirCanvas                                                  │
│  ├─ Bézier-smoothed trail drawing                          │
│  ├─ Effect engine (Glow / Rainbow / Sparkle / Pastel)      │
│  └─ Alpha composite over background                         │
│       │                                                     │
│       ▼                                                     │
│  ParticleSystem                                             │
│  └─ Physics-simulated glow particles                        │
│       │                                                     │
│       ▼                                                     │
│  Streamlit `st.image()` → Browser                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Choices

- **No neural-network gesture classifier** — all gestures are determined from landmark geometry (tip-above-knuckle rules). This keeps the model footprint tiny and inference deterministic.
- **Persistent canvas layer** — drawing accumulates on a separate NumPy array that is alpha-composited over each frame, so strokes survive hand movement.
- **Chaikin smoothing** — raw landmark coordinates are noisy; corner-cutting interpolation produces visually smooth trails.
- **Effect-agnostic trail API** — `AirCanvas.draw_trail()` dispatches to effect-specific private methods, making it trivial to add new effects.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9 – 3.12**
- A working **webcam** (built-in or USB)
- **pip** ≥ 23.0

> **Linux users:** you may need `sudo apt-get install libgl1-mesa-glx libglib2.0-0`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ilyaskhan12Q/air-canvas.git
cd air-canvas

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install runtime dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

Your browser will open at **http://localhost:8501**.

1. Click **▶ Start Camera**
2. Allow browser webcam access if prompted
3. Hold your hand 30–60 cm from the camera
4. Raise your **index finger** to start drawing ✌️

---

## ✌️ Gesture Reference

| Gesture | Hand Shape | Action |
|---------|-----------|--------|
| **Draw** | Index finger extended, others curled | Brush follows fingertip |
| **Draw (V)** | Index + middle extended (peace sign) | Same as Draw |
| **Pause** | Fist (all fingers curled) | Stop drawing, move freely |
| **Erase** | Open palm (all fingers extended) | Erase in a circle around fingertip |
| **Clear** | Thumbs-up (thumb only extended) | Wipe entire canvas |

### Tips for Best Results

- Keep your hand **30–60 cm** from the webcam
- Draw against a **plain, contrasting background**
- Use **good ambient lighting** — avoid direct backlighting
- Make deliberate, **slow-to-medium speed** movements for cleaner lines
- If tracking is jittery, try lowering the confidence thresholds in the sidebar (coming in v1.1)

---

## 🎨 Effect Modes

| Mode | Description |
|------|-------------|
| **Neon Glow** | Bright core + concentric glow rings — the classic cyberpunk look |
| **Rainbow** | Hue cycles through the spectrum as you draw |
| **Sparkle** | Main stroke + random white star particles scattered along the trail |
| **Pastel** | Soft, desaturated tones for a gentle watercolour feel |
| **Classic** | Clean anti-aliased line — no extra effects |

---

## 📁 Project Structure

```
air-canvas/
│
├── app.py                          # Streamlit application entry point
│
├── src/
│   ├── __init__.py
│   ├── hand_tracker.py             # MediaPipe Hands wrapper + landmark types
│   ├── canvas.py                   # AirCanvas: drawing, effects, compositing
│   ├── gesture.py                  # GestureRecognizer: rule-based classifier
│   └── effects.py                  # ParticleSystem: physics particles
│
├── tests/
│   ├── __init__.py
│   ├── test_hand_tracker.py
│   ├── test_gesture.py
│   └── test_canvas.py
│
├── assets/
│   └── demo.gif                    # Demo recording (add your own)
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml                  # CI: lint → test (3 OS × 4 Python)
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── pyproject.toml                  # Build config + Ruff/Black/mypy/pytest
├── requirements.txt                # Runtime deps
├── requirements-dev.txt            # Dev + test deps
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── SECURITY.md
└── .gitignore
```

---

## 🔧 Configuration

All runtime settings are exposed in the **Streamlit sidebar** — no config files needed.

For advanced tuning, edit the `HandTracker` constructor in `app.py`:

```python
tracker = HandTracker(
    max_hands=1,           # increase to 2 for two-hand drawing
    detection_conf=0.7,    # lower if detection is slow to trigger
    tracking_conf=0.7,     # lower if tracking is jittery
)
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/test_gesture.py -v

# Lint
ruff check src/ tests/ app.py

# Format check
black --check src/ tests/ app.py
```

### CI Matrix

Every push and pull-request runs the full test suite across:

| OS | Python versions |
|----|----------------|
| Ubuntu 22.04 | 3.9, 3.10, 3.11, 3.12 |
| Windows Server 2022 | 3.9, 3.10, 3.11, 3.12 |
| macOS 14 (Sonoma) | 3.9, 3.10, 3.11, 3.12 |

---

## 🐳 Docker

```dockerfile
# Dockerfile (create this in project root)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

```bash
docker build -t air-canvas .
docker run -p 8501:8501 --device=/dev/video0 air-canvas
```

> Note: webcam passthrough requires `--device=/dev/video0` (Linux) or extra Docker Desktop configuration on macOS/Windows.

---

## 🛣️ Roadmap

- [ ] **v1.1** — Adjustable detection/tracking confidence sliders in UI
- [ ] **v1.1** — Two-hand drawing (one hand draws, other controls colour)
- [ ] **v1.2** — Shape recognition (circles, squares auto-completed)
- [ ] **v1.2** — Undo / redo stack (pinch gesture)
- [ ] **v1.3** — Save artwork as PNG / SVG
- [ ] **v1.3** — Timelapse playback of a drawing session
- [ ] **v2.0** — WebRTC mode (`streamlit-webrtc`) for cloud deployment
- [ ] **v2.0** — Multiplayer canvas (multiple users draw together via WebSocket)

---

## 🤝 Contributing

We love contributions! Please read [**CONTRIBUTING.md**](CONTRIBUTING.md) before opening a PR.

Short version:

```bash
git checkout -b feat/your-feature
# ... make changes, add tests ...
black src/ tests/ app.py && ruff check src/ tests/ app.py
pytest
git commit -m "feat(scope): what you did"
git push origin feat/your-feature
# Open PR against main
```

---

## 🔒 Security

Please **do not** open public issues for security vulnerabilities.  
See [**SECURITY.md**](SECURITY.md) for the responsible-disclosure process.

---

## 📄 License

Distributed under the **MIT License**. See [**LICENSE**](LICENSE) for full text.

---

## 🙏 Acknowledgements

- [**MediaPipe**](https://mediapipe.dev/) by Google — the hand landmark detection backbone
- [**OpenCV**](https://opencv.org/) — frame capture, drawing primitives, compositing
- [**Streamlit**](https://streamlit.io/) — the browser UI framework
- Inspired by the original air-drawing demos circulating in the computer-vision community

---

<div align="center">

Made with ❤️ and 🤚 gestures

⭐ **Star this repo if you found it useful!**

</div>
