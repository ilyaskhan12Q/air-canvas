"""
AirCanvas — persistent drawing layer with multi-effect rendering.
"""

from __future__ import annotations

import cv2
import numpy as np
import colorsys
import math
from collections import deque
from typing import Deque, Tuple


Color = Tuple[int, int, int]   # BGR


class AirCanvas:
    """
    Manages a transparent drawing canvas that is composited over the
    camera / background frame every tick.

    Coordinates are in pixels matching the source frame dimensions.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width  = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw_trail(
        self,
        trail: Deque[Tuple[int, int]],
        color: Color,
        brush_size: int,
        effect_mode: str,
    ) -> None:
        """Draw smooth Bézier-interpolated trail with optional glow."""
        pts = list(trail)
        if len(pts) < 2:
            return

        # Smooth the trail with interpolation
        smooth = self._smooth_points(pts)

        for i in range(1, len(smooth)):
            p1, p2 = smooth[i - 1], smooth[i]

            if effect_mode == "Neon Glow":
                self._draw_glow(p1, p2, color, brush_size)
            elif effect_mode == "Rainbow":
                hue = (i / len(smooth)) % 1.0
                rainbow_col = self._hsv_to_bgr(hue, 1.0, 1.0)
                self._draw_glow(p1, p2, rainbow_col, brush_size)
            elif effect_mode == "Sparkle":
                self._draw_sparkle(p1, p2, color, brush_size)
            elif effect_mode == "Pastel":
                pastel = self._pastelify(color)
                cv2.line(self.canvas, p1, p2, pastel, brush_size,
                         lineType=cv2.LINE_AA)
            else:  # Classic
                cv2.line(self.canvas, p1, p2, color, brush_size,
                         lineType=cv2.LINE_AA)

    def erase(self, x: int, y: int, radius: int = 40) -> None:
        """Erase a circular region from the canvas."""
        cv2.circle(self.canvas, (x, y), radius, (0, 0, 0), -1)

    def clear(self) -> None:
        """Wipe the entire canvas."""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    # ── Compositing ───────────────────────────────────────────────────────────

    def composite(self, background: np.ndarray) -> np.ndarray:
        """
        Alpha-blend the canvas over a background frame.
        Canvas pixels that are black (0,0,0) are treated as transparent.
        """
        mask = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 5, 255, cv2.THRESH_BINARY)

        output = background.copy()
        mask_inv = cv2.bitwise_not(mask)
        bg_part  = cv2.bitwise_and(output, output, mask=mask_inv)
        fg_part  = cv2.bitwise_and(self.canvas, self.canvas, mask=mask)
        output   = cv2.add(bg_part, fg_part)
        return output

    # ── Effect helpers ────────────────────────────────────────────────────────

    def _draw_glow(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        color: Color,
        size: int,
    ) -> None:
        """Draw a line with concentric blurred glow rings."""
        # Outer soft glow
        for width, alpha in [(size + 10, 0.08), (size + 6, 0.15), (size + 2, 0.4)]:
            glow_col = tuple(int(c * alpha) for c in color)
            cv2.line(self.canvas, p1, p2, glow_col, width, lineType=cv2.LINE_AA)
        # Core bright line
        cv2.line(self.canvas, p1, p2, color, size, lineType=cv2.LINE_AA)
        # White hot centre
        if size > 2:
            cv2.line(self.canvas, p1, p2, (255, 255, 255), max(1, size // 3),
                     lineType=cv2.LINE_AA)

    def _draw_sparkle(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        color: Color,
        size: int,
    ) -> None:
        """Draw main line with random star sparkles along it."""
        cv2.line(self.canvas, p1, p2, color, size, lineType=cv2.LINE_AA)
        # Random sparkle dots
        num = np.random.randint(0, 3)
        for _ in range(num):
            t  = np.random.random()
            sx = int(p1[0] + t * (p2[0] - p1[0]) + np.random.randint(-10, 10))
            sy = int(p1[1] + t * (p2[1] - p1[1]) + np.random.randint(-10, 10))
            sr = np.random.randint(1, 4)
            cv2.circle(self.canvas, (sx, sy), sr, (255, 255, 255), -1)

    @staticmethod
    def _smooth_points(
        pts: list, factor: float = 0.4
    ) -> list:
        """Simple Chaikin corner-cutting smoothing."""
        if len(pts) < 3:
            return pts
        smooth = [pts[0]]
        for i in range(len(pts) - 1):
            p0 = pts[i]
            p1 = pts[i + 1]
            q = (
                int(p0[0] + factor * (p1[0] - p0[0])),
                int(p0[1] + factor * (p1[1] - p0[1])),
            )
            r = (
                int(p1[0] - factor * (p1[0] - p0[0])),
                int(p1[1] - factor * (p1[1] - p0[1])),
            )
            smooth.extend([q, r])
        smooth.append(pts[-1])
        return smooth

    @staticmethod
    def _hsv_to_bgr(h: float, s: float, v: float) -> Color:
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(b * 255), int(g * 255), int(r * 255))

    @staticmethod
    def _pastelify(color: Color) -> Color:
        return tuple(min(255, int(c * 0.6 + 100)) for c in color)

    # ── Convenience ───────────────────────────────────────────────────────────

    def get_effect_color(
        self,
        base_color: Color,
        effect_mode: str,
        frame_index: int,
    ) -> Color:
        """Return the draw color for the current frame given the effect mode."""
        if effect_mode == "Rainbow":
            hue = (frame_index % 180) / 180.0
            return self._hsv_to_bgr(hue, 1.0, 1.0)
        return base_color
