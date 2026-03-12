"""Tests for AirCanvas."""

import numpy as np
import pytest
from collections import deque
from src.canvas import AirCanvas


class TestAirCanvas:
    def setup_method(self):
        self.canvas = AirCanvas(width=640, height=480)

    def test_canvas_initialized_black(self):
        assert self.canvas.canvas.shape == (480, 640, 3)
        assert self.canvas.canvas.sum() == 0

    def test_clear_wipes_canvas(self):
        # Paint something
        self.canvas.canvas[100, 100] = (255, 255, 255)
        self.canvas.clear()
        assert self.canvas.canvas.sum() == 0

    def test_erase_removes_pixels(self):
        self.canvas.canvas[100, 100] = (255, 0, 0)
        self.canvas.erase(100, 100, radius=5)
        assert self.canvas.canvas[100, 100].sum() == 0

    def test_composite_shape(self):
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        out = self.canvas.composite(bg)
        assert out.shape == (480, 640, 3)

    def test_draw_trail_classic(self):
        trail = deque([(100, 100), (110, 110), (120, 120)])
        self.canvas.draw_trail(trail, color=(0, 255, 0), brush_size=3, effect_mode="Classic")
        # Canvas should no longer be all-black
        assert self.canvas.canvas.sum() > 0

    def test_get_effect_color_rainbow(self):
        color = self.canvas.get_effect_color((0, 255, 0), "Rainbow", frame_index=30)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)

    def test_get_effect_color_default(self):
        base = (100, 150, 200)
        color = self.canvas.get_effect_color(base, "Classic", frame_index=0)
        assert color == base

    @pytest.mark.parametrize("mode", ["Neon Glow", "Rainbow", "Sparkle", "Pastel", "Classic"])
    def test_draw_trail_all_effects(self, mode):
        canvas = AirCanvas(640, 480)
        trail = deque([(50, 50), (60, 60), (70, 50), (80, 60)])
        canvas.draw_trail(trail, color=(0, 245, 212), brush_size=4, effect_mode=mode)
