"""Air Canvas — source package."""

from src.hand_tracker import HandTracker
from src.canvas import AirCanvas
from src.gesture import GestureRecognizer
from src.effects import ParticleSystem
from src.model_downloader import ensure_model

__all__ = ["HandTracker", "AirCanvas", "GestureRecognizer", "ParticleSystem", "ensure_model"]
__version__ = "1.0.0"
