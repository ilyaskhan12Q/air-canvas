"""Tests for GestureRecognizer."""

import pytest
from src.hand_tracker import LandmarkPoint
from src.gesture import GestureRecognizer


def _make_hand(finger_states: list) -> list:
    """
    Build a minimal 21-landmark hand where fingers are extended/curled
    based on finger_states = [thumb, index, middle, ring, pinky].

    Strategy:
      - For each finger (excluding thumb): tip.y = base.y - 0.2 if up, else base.y + 0.2
      - Thumb: tip.x = base.x - 0.2 if up, else base.x + 0.2
    """
    # 21 neutral landmarks at y=0.5
    lms = [LandmarkPoint(0.5, 0.5, 0.0) for _ in range(21)]

    tips   = [4,  8, 12, 16, 20]
    joints = [3,  6, 10, 14, 18]

    thumb_up, *others = finger_states

    # Thumb (x-axis)
    lms[joints[0]] = LandmarkPoint(0.5, 0.5, 0.0)
    lms[tips[0]]   = LandmarkPoint(0.3 if thumb_up else 0.7, 0.5, 0.0)

    # Other fingers (y-axis)
    for i, (up, tip_i, joint_i) in enumerate(zip(others, tips[1:], joints[1:])):
        lms[joint_i] = LandmarkPoint(0.5, 0.5, 0.0)
        lms[tip_i]   = LandmarkPoint(0.5, 0.3 if up else 0.7, 0.0)

    return lms


class TestGestureRecognizer:
    def setup_method(self):
        self.rec = GestureRecognizer()

    def test_draw_index_only(self):
        lms = _make_hand([False, True, False, False, False])
        assert self.rec.recognize(lms) == "DRAW"

    def test_draw_peace_sign(self):
        lms = _make_hand([False, True, True, False, False])
        assert self.rec.recognize(lms) == "DRAW"

    def test_pause_fist(self):
        lms = _make_hand([False, False, False, False, False])
        assert self.rec.recognize(lms) == "PAUSE"

    def test_erase_open_palm(self):
        lms = _make_hand([True, True, True, True, True])
        assert self.rec.recognize(lms) == "ERASE"

    def test_clear_thumbs_up(self):
        lms = _make_hand([True, False, False, False, False])
        assert self.rec.recognize(lms) == "CLEAR"

    def test_description_returns_string(self):
        for gesture in ["DRAW", "PAUSE", "ERASE", "CLEAR", "UNKNOWN"]:
            desc = self.rec.gesture_description(gesture)
            assert isinstance(desc, str)
            assert len(desc) > 0
