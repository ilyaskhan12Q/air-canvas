"""
model_downloader.py — Downloads the MediaPipe hand landmarker task file on first run.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path


MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = Path(__file__).parent / "assets" / "hand_landmarker.task"


def ensure_model() -> Path:
    """
    Download the hand landmarker model if it doesn't already exist.

    Returns
    -------
    Path
        Absolute path to the local .task file.
    """
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists():
        return MODEL_PATH

    print(f"[Air Canvas] Downloading hand landmark model → {MODEL_PATH}")
    print("             (this only happens once, ~5 MB)")

    try:
        def _progress(count, block_size, total):
            pct = min(100, int(count * block_size * 100 / total))
            print(f"\r  Downloading... {pct}%", end="", flush=True)

        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=_progress)
        print("\r  ✅ Model downloaded successfully.          ")
    except Exception as exc:
        raise RuntimeError(
            f"Failed to download the MediaPipe hand landmark model.\n"
            f"URL: {MODEL_URL}\n"
            f"Error: {exc}\n\n"
            f"You can also download it manually and place it at:\n"
            f"  {MODEL_PATH}"
        ) from exc

    return MODEL_PATH
