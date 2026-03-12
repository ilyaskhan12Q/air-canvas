"""
Hand Tracker — MediaPipe Tasks-based real-time hand landmark detection.

Compatible with mediapipe >= 0.10.14 (new Tasks API).
The legacy mp.solutions.hands API was removed in newer versions.
"""

from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from src.model_downloader import ensure_model


@dataclass
class LandmarkPoint:
    x: float   # normalized [0, 1]
    y: float   # normalized [0, 1]
    z: float   # depth (relative)


# Hand landmark indices (same numbering as legacy API)
FINGERTIPS   = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky
FINGER_BASES = [2, 5,  9, 13, 17]   # MCP joints
KNUCKLES     = [3, 6, 10, 14, 18]   # PIP joints
WRIST        = 0

# Connection pairs for manual skeleton drawing
HAND_CONNECTIONS: List[Tuple[int, int]] = [
    (0,1),(1,2),(2,3),(3,4),         # thumb
    (0,5),(5,6),(6,7),(7,8),         # index
    (5,9),(9,10),(10,11),(11,12),    # middle
    (9,13),(13,14),(14,15),(15,16),  # ring
    (13,17),(17,18),(18,19),(19,20), # pinky
    (0,17),                          # palm base
]


class HandTracker:
    """
    Wraps the MediaPipe Hand Landmarker Task for single/multi-hand detection.

    Uses the new Tasks API (mediapipe >= 0.10.14). The model file is
    downloaded automatically on first use (~5 MB).

    Parameters
    ----------
    max_hands : int
        Maximum number of hands to detect (1 or 2).
    detection_conf : float
        Minimum confidence for initial detection [0, 1].
    tracking_conf : float
        Minimum confidence for tracking [0, 1].
    """

    def __init__(
        self,
        max_hands: int = 1,
        detection_conf: float = 0.7,
        tracking_conf: float = 0.7,
    ) -> None:
        model_path = ensure_model()

        base_options = mp_python.BaseOptions(
            model_asset_path=str(model_path)
        )
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)

        # Neon draw colours for skeleton overlay (BGR)
        self._landmark_color   = (0, 245, 212)   # cyan
        self._connection_color = (247, 37, 133)  # pink

    # ──────────────────────────────────────────────────────────────────────────

    def process(
        self,
        frame: np.ndarray,
    ) -> Tuple[Optional[List[LandmarkPoint]], Optional[np.ndarray]]:
        """
        Detect hand landmarks in a BGR frame.

        Returns
        -------
        landmarks : list[LandmarkPoint] | None
            21 landmarks for the first detected hand, or None.
        annotated : np.ndarray | None
            BGR frame with neon skeleton drawn on a black canvas, or None.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self._landmarker.detect(mp_image)

        if not result.hand_landmarks:
            return None, None

        # Use first detected hand
        raw_lms   = result.hand_landmarks[0]
        landmarks = [
            LandmarkPoint(x=lm.x, y=lm.y, z=lm.z)
            for lm in raw_lms
        ]

        # Draw neon skeleton onto a black canvas
        h, w = frame.shape[:2]
        annotated = np.zeros((h, w, 3), dtype=np.uint8)

        for start_idx, end_idx in HAND_CONNECTIONS:
            p1 = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
            p2 = (int(landmarks[end_idx].x * w),   int(landmarks[end_idx].y * h))
            cv2.line(annotated, p1, p2, self._connection_color, 2, lineType=cv2.LINE_AA)

        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(annotated, (cx, cy), 4, self._landmark_color,  -1, lineType=cv2.LINE_AA)
            cv2.circle(annotated, (cx, cy), 5, (255, 255, 255),        1, lineType=cv2.LINE_AA)

        return landmarks, annotated

    # ──────────────────────────────────────────────────────────────────────────

    def get_pixel_coords(
        self,
        landmarks: List[LandmarkPoint],
        frame_width: int,
        frame_height: int,
        index: int,
    ) -> Tuple[int, int]:
        """Convert a normalized landmark to pixel coordinates."""
        lm = landmarks[index]
        return int(lm.x * frame_width), int(lm.y * frame_height)

    def finger_states(self, landmarks: List[LandmarkPoint]) -> List[bool]:
        """
        Return [thumb_up, index_up, middle_up, ring_up, pinky_up].
        A finger is 'up' when its tip is above its DIP joint (in image y-coords).
        """
        tips   = [4,  8, 12, 16, 20]
        joints = [3,  6, 10, 14, 18]
        states = []

        # Thumb: compare x (left = extended for right hand facing camera)
        states.append(landmarks[tips[0]].x < landmarks[joints[0]].x)

        # Other fingers: tip.y < joint.y  →  pointing up
        for tip, joint in zip(tips[1:], joints[1:]):
            states.append(landmarks[tip].y < landmarks[joint].y)

        return states

    def close(self) -> None:
        self._landmarker.close()
