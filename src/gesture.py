"""
Gesture Recognizer — maps hand landmarks to high-level gestures.

Gesture vocabulary
------------------
DRAW    — index finger extended, others curled  → draw brush
PAUSE   — fist (all fingers curled)             → stop drawing
ERASE   — open palm (all fingers extended)      → erase
CLEAR   — thumbs-up                             → clear canvas
UNKNOWN — any other configuration
"""

from __future__ import annotations

from typing import List

from src.hand_tracker import LandmarkPoint, FINGERTIPS


class GestureRecognizer:
    """
    Rule-based gesture classifier using hand landmark geometry.

    All recognition is purely geometric — no ML model is required beyond
    the MediaPipe landmark detection upstream.
    """

    # ── Public API ────────────────────────────────────────────────────────────

    def recognize(self, landmarks: List[LandmarkPoint]) -> str:
        """
        Classify a gesture from 21 hand landmarks.

        Parameters
        ----------
        landmarks : list of LandmarkPoint
            Output from HandTracker.process().

        Returns
        -------
        str
            One of: DRAW | PAUSE | ERASE | CLEAR | UNKNOWN
        """
        states = self._finger_states(landmarks)
        thumb, index, middle, ring, pinky = states

        # Open palm → Erase
        if all(states):
            return "ERASE"

        # Thumbs-up: thumb up, all others down → Clear
        if thumb and not index and not middle and not ring and not pinky:
            return "CLEAR"

        # Index only → Draw
        if not thumb and index and not middle and not ring and not pinky:
            return "DRAW"

        # Peace/V sign → Draw (also common for drawing)
        if not thumb and index and middle and not ring and not pinky:
            return "DRAW"

        # Fist → Pause
        if not any(states):
            return "PAUSE"

        return "UNKNOWN"

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _finger_states(landmarks: List[LandmarkPoint]) -> List[bool]:
        """
        Determine which fingers are extended.
        Returns [thumb, index, middle, ring, pinky] as booleans.
        """
        tips   = [4,  8, 12, 16, 20]
        joints = [3,  6, 10, 14, 18]   # DIP joints (one below tip)
        states = []

        # Thumb: compare x position (works for right hand facing camera)
        tip_x  = landmarks[tips[0]].x
        base_x = landmarks[joints[0]].x
        states.append(tip_x < base_x)

        # Other fingers: tip y < joint y  →  finger pointing up
        for tip_i, joint_i in zip(tips[1:], joints[1:]):
            states.append(landmarks[tip_i].y < landmarks[joint_i].y)

        return states

    def gesture_description(self, gesture: str) -> str:
        """Human-readable description for a gesture code."""
        descriptions = {
            "DRAW":    "✌️ Drawing — index finger is your brush",
            "PAUSE":   "✊ Paused — make a fist to stop drawing",
            "ERASE":   "🖐️ Erasing — open palm erases nearby strokes",
            "CLEAR":   "👍 Clearing — thumbs-up clears the canvas",
            "UNKNOWN": "❓ Gesture not recognized",
        }
        return descriptions.get(gesture, descriptions["UNKNOWN"])
