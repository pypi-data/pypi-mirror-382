from importlib.metadata import PackageNotFoundError, version
from .scene import Scene
from .shapes import Circle, Rectangle, Line, Text
from .animation import Animation, MoveTo, FadeIn, FadeOut, ScaleTo

__all__ = [
    "Scene",
    "Circle",
    "Rectangle",
    "Line",
    "Text",
    "Animation",
    "MoveTo",
    "FadeIn",
    "FadeOut",
    "ScaleTo",
]

try:  # Resolve installed version; fallback when running from source without metadata
    __version__ = version("picoanim")
except PackageNotFoundError:  # pragma: no cover - during local dev before install
    __version__ = "0.0.0"
