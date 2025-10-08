from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .easing import EASING
from .mobject import MObject


@dataclass
class Animation:
    target: MObject
    duration: float = 1.0
    easing: str = "linear"
    _start: Dict[str, float] = field(default_factory=dict, init=False, repr=False)
    _end: Dict[str, float] = field(default_factory=dict, init=False, repr=False)

    def prepare(self, start_state: Dict[str, float]) -> None:
        # Called by Scene when added to a segment; captures start state
        self._start = dict(start_state)

    def set_end(self, end_state: Dict[str, float]) -> None:
        self._end = dict(end_state)

    def ease(self, t: float) -> float:
        f = EASING.get(self.easing, EASING["linear"])
        return f(t)

    def apply_at(self, alpha: float) -> None:
        t = max(0.0, min(1.0, float(alpha)))
        e = self.ease(t)
        for k, v0 in self._start.items():
            if k in self._end:
                v1 = self._end[k]
                if isinstance(v0, (float, int)) and isinstance(v1, (float, int)):
                    val = (1 - e) * float(v0) + e * float(v1)
                    setattr(self.target, k, val)
        # visibility passes through from end at final frame
        if t >= 1.0 and "visible" in self._end:
            self.target.visible = bool(self._end["visible"])


class MoveTo(Animation):
    def __init__(self, target: MObject, point: tuple[float, float], duration: float = 1.0, easing: str = "linear"):
        super().__init__(target, duration, easing)
        self.tx = float(point[0])
        self.ty = float(point[1])

    def configure(self, start_state: Dict[str, float]) -> None:
        self.prepare(start_state)
        self.set_end({**start_state, "x": self.tx, "y": self.ty})


class FadeIn(Animation):
    def __init__(self, target: MObject, duration: float = 0.8, easing: str = "linear"):
        super().__init__(target, duration, easing)

    def configure(self, start_state: Dict[str, float]) -> None:
        new_start = dict(start_state)
        new_start["opacity"] = 0.0
        new_end = dict(start_state)
        new_end["opacity"] = 1.0
        new_end["visible"] = True
        self.prepare(new_start)
        self.set_end(new_end)


class FadeOut(Animation):
    def __init__(self, target: MObject, duration: float = 0.8, easing: str = "linear"):
        super().__init__(target, duration, easing)

    def configure(self, start_state: Dict[str, float]) -> None:
        new_end = dict(start_state)
        new_end["opacity"] = 0.0
        new_end["visible"] = True  # keep drawn while fading
        self.prepare(start_state)
        self.set_end(new_end)


class ScaleTo(Animation):
    def __init__(self, target: MObject, scale: float, duration: float = 0.6, easing: str = "linear"):
        super().__init__(target, duration, easing)
        self.tscale = float(scale)

    def configure(self, start_state: Dict[str, float]) -> None:
        self.prepare(start_state)
        self.set_end({**start_state, "scale": self.tscale})
