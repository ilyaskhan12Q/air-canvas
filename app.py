"""
✋ Air Canvas — Real-time Hand Gesture Drawing App
Architecture:
  - A background thread owns cv2.VideoCapture and runs the full pipeline
  - The Streamlit main thread reads the latest JPEG bytes and calls st.image()
  - Frames are encoded as JPEG bytes → NO MediaFileStorageError
  - Camera index is auto-detected by trying 0..4 then /dev/video*
"""

import io
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from src.canvas import AirCanvas
from src.effects import ParticleSystem
from src.gesture import GestureRecognizer
from src.hand_tracker import HandTracker

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="✋ Air Canvas",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0e0e0e 0%, #1a1a2e 100%); }
.title-text {
    font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(90deg, #00f5d4, #f72585, #7209b7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; text-align: center;
}
.subtitle-text { color: #aaa; font-size: 1.05rem; text-align: center; margin-top:-0.4rem; }
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 0.8rem; text-align: center; margin-bottom:0.5rem;
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #00f5d4; }
.metric-label { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
.gesture-tag {
    background: rgba(0,245,212,0.1); border: 1px solid #00f5d4;
    border-radius: 20px; padding: 4px 12px; color: #00f5d4;
    font-size: 0.85rem; display: inline-block; margin: 3px;
}
.stButton>button {
    background: linear-gradient(135deg, #00f5d4, #7209b7);
    color: white; border: none; border-radius: 8px;
    font-weight: 600; padding: 0.5rem 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Camera auto-detection
# ─────────────────────────────────────────────────────────────────────────────
def find_camera() -> int:
    """
    Try camera indices 0..4 and any /dev/video* device.
    Returns the first working index, or -1 if none found.
    """
    candidates = list(range(5))

    # Also try explicit /dev/video* paths on Linux
    import glob
    for p in sorted(glob.glob("/dev/video*")):
        try:
            idx = int(p.replace("/dev/video", ""))
            if idx not in candidates:
                candidates.append(idx)
        except ValueError:
            pass

    for idx in candidates:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                return idx
    return -1


# ─────────────────────────────────────────────────────────────────────────────
# Shared state between background thread and Streamlit main thread
# ─────────────────────────────────────────────────────────────────────────────
class CameraState:
    """Thread-safe container for the latest processed frame + pipeline objects."""

    def __init__(self):
        self._lock         = threading.Lock()
        self._jpeg_bytes   = None          # latest encoded frame (bytes)
        self._running      = False
        self._thread       = None
        self.error_msg     = ""

        # Stats (written by bg thread, read by main thread — best-effort)
        self.fps           = 0.0
        self.strokes       = 0
        self.gesture       = "—"
        self.frame_idx     = 0

        # Pipeline objects live here (created once in bg thread)
        self.tracker       = None
        self.recognizer    = None
        self.particles     = None
        self.canvas        = None
        self.trail         = None

    # ── Frame exchange ────────────────────────────────────────────────────────
    def put_frame(self, jpeg: bytes):
        with self._lock:
            self._jpeg_bytes = jpeg

    def get_frame(self) -> bytes | None:
        with self._lock:
            return self._jpeg_bytes

    # ── Control ───────────────────────────────────────────────────────────────
    @property
    def running(self) -> bool:
        return self._running

    def start(self):
        if self._running:
            return
        self._running = True
        self.error_msg = ""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def clear_canvas(self):
        if self.canvas:
            self.canvas.clear()
            if self.trail:
                self.trail.clear()
            self.strokes = 0

    # ── Background pipeline loop ──────────────────────────────────────────────
    def _run(self):
        cam_idx = find_camera()
        if cam_idx == -1:
            self.error_msg = (
                "❌ No webcam found.\n\n"
                "Tried indices 0-4 and /dev/video*.\n"
                "• Make sure your camera is plugged in\n"
                "• On Linux run: ls /dev/video*\n"
                "• Try: sudo chmod 666 /dev/video0"
            )
            self._running = False
            return

        cap = cv2.VideoCapture(cam_idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  720)
        cap.set(cv2.CAP_PROP_FPS,            30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,      1)   # minimize latency

        W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Initialise pipeline objects once
        self.tracker    = HandTracker(max_hands=1, detection_conf=0.7, tracking_conf=0.7)
        self.recognizer = GestureRecognizer()
        self.particles  = ParticleSystem(max_particles=300)
        self.canvas     = AirCanvas(W, H)
        self.trail      = deque(maxlen=st.session_state.get("trail_length", 40))

        BG_COLORS = {
            "Black":      (0,   0,   0),
            "Dark Blue":  (10,  10,  30),
            "Dark Green": (5,   20,  10),
        }

        t_prev = time.time()

        while self._running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            self.frame_idx += 1

            # ── Read settings (snapshot from session_state) ──────────────────
            brush_color    = st.session_state.get("brush_color",    (0, 245, 212))
            brush_size     = st.session_state.get("brush_size",     4)
            effect_mode    = st.session_state.get("effect_mode",    "Neon Glow")
            bg_mode        = st.session_state.get("bg_mode",        "Black")
            trail_length   = st.session_state.get("trail_length",   40)
            show_skeleton  = st.session_state.get("show_skeleton",  True)
            show_particles = st.session_state.get("show_particles", True)
            shape_mode     = st.session_state.get("shape_mode",     "Free Draw")
            eraser_mode    = (shape_mode == "Eraser")
            paused         = (shape_mode == "Pause")

            # Handle clear flag
            if st.session_state.get("clear_flag", False):
                self.canvas.clear()
                self.trail.clear()
                self.strokes = 0
                st.session_state["clear_flag"] = False

            # Update trail length dynamically
            if self.trail.maxlen != trail_length:
                self.trail = deque(list(self.trail), maxlen=trail_length)

            # ── Background layer ─────────────────────────────────────────────
            if bg_mode in BG_COLORS:
                bg = np.full((H, W, 3), BG_COLORS[bg_mode], dtype=np.uint8)
            else:  # Mirror Feed
                bg = frame.copy()

            # ── Hand tracking ────────────────────────────────────────────────
            landmarks, annotated = self.tracker.process(frame)

            if landmarks:
                gesture = self.recognizer.recognize(landmarks)
                self.gesture = gesture

                ix = int(landmarks[8].x * W)
                iy = int(landmarks[8].y * H)

                if gesture == "DRAW" and not eraser_mode and not paused:
                    self.trail.append((ix, iy))
                    color = self.canvas.get_effect_color(brush_color, effect_mode, self.frame_idx)
                    self.canvas.draw_trail(self.trail, color, brush_size, effect_mode)
                    if show_particles:
                        self.particles.emit(ix, iy, color, 3)
                    self.strokes += 1

                elif gesture == "ERASE":
                    self.trail.clear()
                    self.canvas.erase(ix, iy, radius=40)

                elif gesture == "CLEAR":
                    self.canvas.clear()
                    self.trail.clear()
                    self.strokes = 0

                elif gesture in ("PAUSE", "UNKNOWN"):
                    self.trail.clear()

                # Fingertip cursor dot
                cv2.circle(bg, (ix, iy), brush_size + 4, brush_color, -1)
                cv2.circle(bg, (ix, iy), brush_size + 6, (255, 255, 255), 1)
            else:
                self.trail.clear()
                self.gesture = "—"

            # ── Composite ────────────────────────────────────────────────────
            output = self.canvas.composite(bg)

            if show_particles:
                self.particles.update()
                self.particles.render(output)

            if show_skeleton and landmarks and annotated is not None:
                output = cv2.addWeighted(output, 1.0, annotated, 0.4, 0)

            # ── HUD overlay ──────────────────────────────────────────────────
            br, bg_c, bb = brush_color
            cv2.putText(output, f"Gesture: {self.gesture}",
                        (15, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (br, bg_c, bb), 2, cv2.LINE_AA)
            cv2.putText(output, f"Mode: {effect_mode}",
                        (15, H - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1, cv2.LINE_AA)

            now = time.time()
            self.fps = 1.0 / max(now - t_prev, 1e-6)
            t_prev = now
            fps_txt = f"FPS: {self.fps:.0f}"
            cv2.putText(output, fps_txt,
                        (W - 110, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2, cv2.LINE_AA)

            # ── Encode to JPEG bytes (avoids Streamlit MediaFileStorageError) ─
            output_rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
            ok, buf = cv2.imencode(".jpg", output_rgb, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ok:
                self.put_frame(buf.tobytes())

        cap.release()
        self._running = False


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    defaults = dict(
        brush_color=(0, 245, 212),
        brush_size=4,
        effect_mode="Neon Glow",
        bg_mode="Black",
        trail_length=40,
        show_skeleton=True,
        show_particles=True,
        shape_mode="Free Draw",
        clear_flag=False,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "cam_state" not in st.session_state:
        st.session_state["cam_state"] = CameraState()

_init()
cam: CameraState = st.session_state["cam_state"]


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="title-text">✋ Air Canvas</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-text">Real-time Hand Gesture Drawing · MediaPipe + OpenCV + Streamlit</div>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📖 Gesture Guide", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("**✌️ Index Finger Up**\nDraw mode")
    c2.markdown("**✊ Fist**\nPause — move without drawing")
    c3.markdown("**🖐️ Open Palm**\nErase nearby strokes")
    c4.markdown("**👍 Thumbs Up**\nClear entire canvas")

st.divider()

# ── Layout ────────────────────────────────────────────────────────────────────
main_col, ctrl_col = st.columns([3, 1])

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎨 Canvas Controls")
    st.divider()

    st.markdown("### 🖌️ Brush Color")
    palette = {
        "Cyan":   (0, 245, 212), "Pink":   (247, 37, 133),
        "Purple": (114, 9, 183), "Yellow": (255, 209, 0),
        "Orange": (255, 100, 0), "White":  (255, 255, 255),
        "Green":  (57, 255, 20), "Red":    (255, 50, 50),
    }
    cols = st.columns(4)
    for i, (name, rgb) in enumerate(palette.items()):
        with cols[i % 4]:
            if st.button("⬤", key=f"c_{name}", help=name):
                st.session_state.brush_color = rgb

    ch = st.color_picker("Custom", "#00f5d4", key="cpicker")
    if st.button("Apply Custom"):
        st.session_state.brush_color = (
            int(ch[1:3], 16), int(ch[3:5], 16), int(ch[5:7], 16)
        )

    st.divider()
    st.markdown("### ✏️ Brush")
    st.session_state.brush_size   = st.slider("Brush Size",   1, 20, st.session_state.brush_size)
    st.session_state.trail_length = st.slider("Trail Length", 5, 100, st.session_state.trail_length)

    st.divider()
    st.markdown("### ✨ Effects")
    st.session_state.effect_mode = st.selectbox(
        "Effect Mode", ["Neon Glow", "Rainbow", "Sparkle", "Pastel", "Classic"]
    )
    st.session_state.bg_mode = st.selectbox(
        "Background", ["Black", "Dark Blue", "Dark Green", "Mirror Feed"]
    )
    st.session_state.show_skeleton  = st.toggle("Show Hand Skeleton", value=True)
    st.session_state.show_particles = st.toggle("Show Particles",     value=True)

    st.divider()
    st.markdown("### 🖱️ Draw Mode")
    st.session_state.shape_mode = st.radio(
        "Mode", ["Free Draw", "Eraser", "Pause"], index=0
    )

    st.divider()
    if st.button("🗑️ Clear Canvas", use_container_width=True):
        st.session_state["clear_flag"] = True

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#555;font-size:0.75rem;'>Air Canvas v1.0.0 · MIT</div>",
        unsafe_allow_html=True,
    )

# ── Main panel ────────────────────────────────────────────────────────────────
with main_col:
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("▶ Start", use_container_width=True):
            cam.start()
    with btn_col2:
        if st.button("⏹ Stop", use_container_width=True):
            cam.stop()
    with btn_col3:
        snap_btn = st.button("📸 Screenshot", use_container_width=True)

    # Error display
    if cam.error_msg:
        st.error(cam.error_msg)

    video_ph = st.empty()

with ctrl_col:
    st.markdown("### 📊 Stats")
    fps_ph     = st.empty()
    stroke_ph  = st.empty()
    gesture_ph = st.empty()
    color_ph   = st.empty()

    st.markdown("### 💡 Tips")
    st.markdown("""
- Hand **30–60 cm** from lens  
- Good lighting = better tracking  
- Use a plain background  
- ✌️ Index = draw  
- ✊ Fist = pause  
- 🖐️ Palm = erase  
- 👍 Thumb = clear  
    """)

# ── Render loop ───────────────────────────────────────────────────────────────
PLACEHOLDER_HTML = """
<div style="
    width:100%; height:420px;
    background:linear-gradient(135deg,#0d0d0d,#1a0533);
    border-radius:16px; border:1px solid rgba(114,9,183,0.4);
    display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:1rem;">
  <div style="font-size:4rem">✋</div>
  <div style="color:#00f5d4;font-size:1.3rem;font-weight:600">
      Click <strong>▶ Start</strong> to begin
  </div>
  <div style="color:#888;font-size:0.9rem;text-align:center;max-width:380px">
      Point your index finger at the camera to draw glowing trails in real time.
  </div>
</div>
"""

if not cam.running:
    video_ph.markdown(PLACEHOLDER_HTML, unsafe_allow_html=True)
else:
    # Spin until the background thread produces the first frame
    deadline = time.time() + 8.0
    while cam.get_frame() is None and cam.running and time.time() < deadline:
        video_ph.info("⏳ Opening camera…")
        time.sleep(0.15)

    if cam.error_msg:
        st.error(cam.error_msg)
        st.stop()

    if cam.get_frame() is None:
        st.error("⚠️ Camera timed out. Check that the device is not in use by another app.")
        cam.stop()
        st.stop()

    # Live display loop — Streamlit re-runs this script every time the page
    # refreshes; we poll for ~3 seconds to stream frames before yielding back.
    POLL_SECS   = 3.0        # how long to stream per Streamlit script run
    FRAME_DELAY = 1 / 30     # target 30 fps display

    deadline = time.time() + POLL_SECS
    while cam.running and time.time() < deadline:
        jpeg = cam.get_frame()
        if jpeg:
            # Pass raw bytes — Streamlit will inline them, no temp-file issues
            video_ph.image(jpeg, channels="RGB", use_container_width=True)

            # Screenshot
            if snap_btn and cam.canvas is not None:
                snap_rgb = cv2.cvtColor(
                    cam.canvas.canvas, cv2.COLOR_BGR2RGB
                )
                ok2, buf2 = cv2.imencode(".png", snap_rgb)
                if ok2:
                    st.sidebar.download_button(
                        "⬇️ Download Snapshot",
                        data=buf2.tobytes(),
                        file_name="air_canvas_snapshot.png",
                        mime="image/png",
                    )

        # Update stats
        br_hex = "#{:02x}{:02x}{:02x}".format(*st.session_state.brush_color)
        fps_ph.markdown(
            f"<div class='metric-card'><div class='metric-value'>{cam.fps:.0f}</div>"
            f"<div class='metric-label'>FPS</div></div>", unsafe_allow_html=True)
        stroke_ph.markdown(
            f"<div class='metric-card'><div class='metric-value'>{cam.strokes}</div>"
            f"<div class='metric-label'>Strokes</div></div>", unsafe_allow_html=True)
        gesture_ph.markdown(
            f"<div class='gesture-tag'>👋 {cam.gesture}</div>", unsafe_allow_html=True)
        color_ph.markdown(
            f"<div style='width:100%;height:52px;border-radius:12px;"
            f"background:{br_hex};border:2px solid rgba(255,255,255,0.2);'></div>",
            unsafe_allow_html=True)

        time.sleep(FRAME_DELAY)

    # Force a rerun so Streamlit loops back and continues streaming
    if cam.running:
        st.rerun()
