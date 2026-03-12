"""
ParticleSystem — lightweight CPU particle effects for the air canvas.
"""

from __future__ import annotations

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple


Color = Tuple[int, int, int]


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float          # current lifetime [0..1]
    decay: float         # life lost per frame
    radius: int
    color: Color
    fade: bool = True    # shrink as life decreases


class ParticleSystem:
    """
    Emits and renders small glowing particles that trail the brush tip.

    Parameters
    ----------
    max_particles : int
        Hard cap on simultaneous particles (keeps CPU usage bounded).
    """

    def __init__(self, max_particles: int = 300) -> None:
        self.max_particles = max_particles
        self._particles: List[Particle] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def emit(
        self,
        x: int,
        y: int,
        color: Color,
        count: int = 4,
    ) -> None:
        """Spawn `count` particles at (x, y)."""
        if len(self._particles) >= self.max_particles:
            # Evict oldest particles to stay under cap
            self._particles = self._particles[count:]

        for _ in range(count):
            angle  = np.random.uniform(0, 2 * np.pi)
            speed  = np.random.uniform(0.5, 3.5)
            decay  = np.random.uniform(0.02, 0.07)
            radius = np.random.randint(1, 5)
            # Slightly randomize the colour
            jitter = lambda c: int(np.clip(c + np.random.randint(-30, 30), 0, 255))
            jcolor = (jitter(color[0]), jitter(color[1]), jitter(color[2]))

            self._particles.append(
                Particle(
                    x=float(x),
                    y=float(y),
                    vx=speed * np.cos(angle),
                    vy=speed * np.sin(angle) - 1.0,  # slight upward drift
                    life=1.0,
                    decay=decay,
                    radius=radius,
                    color=jcolor,
                )
            )

    def update(self) -> None:
        """Advance physics simulation by one frame."""
        alive = []
        for p in self._particles:
            p.x   += p.vx
            p.y   += p.vy
            p.vy  += 0.08   # gravity
            p.life -= p.decay
            if p.life > 0:
                alive.append(p)
        self._particles = alive

    def render(self, frame: np.ndarray) -> None:
        """Draw all live particles onto `frame` in-place."""
        for p in self._particles:
            if p.life <= 0:
                continue
            alpha  = max(0.0, p.life)
            radius = max(1, int(p.radius * alpha)) if p.fade else p.radius
            cx, cy = int(p.x), int(p.y)

            if not (0 <= cx < frame.shape[1] and 0 <= cy < frame.shape[0]):
                continue

            # Blend particle colour with existing pixel
            b, g, r = p.color
            overlay = frame[cy, cx].astype(float)
            blended = (
                int(overlay[0] * (1 - alpha) + b * alpha),
                int(overlay[1] * (1 - alpha) + g * alpha),
                int(overlay[2] * (1 - alpha) + r * alpha),
            )
            cv2.circle(frame, (cx, cy), radius, blended, -1, lineType=cv2.LINE_AA)

    # ── Utility ───────────────────────────────────────────────────────────────

    @property
    def count(self) -> int:
        return len(self._particles)

    def clear(self) -> None:
        self._particles.clear()
