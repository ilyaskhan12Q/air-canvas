"""Tests for HandTracker."""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from src.hand_tracker import HandTracker, LandmarkPoint, FINGERTIPS, HAND_CONNECTIONS


def _make_landmarks(n: int = 21) -> list:
    """Return a list of dummy LandmarkPoint objects."""
    rng = np.random.default_rng(42)
    return [
        LandmarkPoint(x=float(rng.random()), y=float(rng.random()), z=0.0)
        for _ in range(n)
    ]


class TestLandmarkPoint:
    def test_fields(self):
        lm = LandmarkPoint(x=0.5, y=0.3, z=-0.01)
        assert lm.x == 0.5
        assert lm.y == 0.3
        assert lm.z == -0.01


class TestHandConnections:
    def test_connections_are_valid_index_pairs(self):
        for start, end in HAND_CONNECTIONS:
            assert 0 <= start <= 20
            assert 0 <= end <= 20
            assert start != end

    def test_thumb_chain_present(self):
        assert (0, 1) in HAND_CONNECTIONS
        assert (1, 2) in HAND_CONNECTIONS
        assert (2, 3) in HAND_CONNECTIONS
        assert (3, 4) in HAND_CONNECTIONS


class TestHandTrackerMethods:
    """
    Tests for HandTracker helper methods that don't require a live model.
    We instantiate with __new__ to bypass __init__.
    """

    def _get_tracker(self) -> HandTracker:
        tracker = HandTracker.__new__(HandTracker)
        tracker._landmark_color   = (0, 245, 212)
        tracker._connection_color = (247, 37, 133)
        return tracker

    def test_get_pixel_coords(self):
        tracker = self._get_tracker()
        lms = _make_landmarks()
        lms[8] = LandmarkPoint(x=0.5, y=0.5, z=0.0)
        px, py = tracker.get_pixel_coords(lms, frame_width=640, frame_height=480, index=8)
        assert px == 320
        assert py == 240

    def test_finger_states_length(self):
        tracker = self._get_tracker()
        lms = _make_landmarks()
        states = tracker.finger_states(lms)
        assert len(states) == 5

    def test_finger_states_returns_booleans(self):
        tracker = self._get_tracker()
        lms = _make_landmarks()
        states = tracker.finger_states(lms)
        for s in states:
            assert isinstance(s, bool)

    def test_finger_up_when_tip_above_joint(self):
        tracker = self._get_tracker()
        lms = _make_landmarks()
        # Index tip (8) above DIP joint (6) → index should be UP
        lms[8] = LandmarkPoint(x=0.5, y=0.2, z=0.0)
        lms[6] = LandmarkPoint(x=0.5, y=0.5, z=0.0)
        states = tracker.finger_states(lms)
        assert states[1] is True  # index finger

    def test_finger_down_when_tip_below_joint(self):
        tracker = self._get_tracker()
        lms = _make_landmarks()
        # Index tip (8) below DIP joint (6) → index should be DOWN
        lms[8] = LandmarkPoint(x=0.5, y=0.8, z=0.0)
        lms[6] = LandmarkPoint(x=0.5, y=0.5, z=0.0)
        states = tracker.finger_states(lms)
        assert states[1] is False  # index finger
