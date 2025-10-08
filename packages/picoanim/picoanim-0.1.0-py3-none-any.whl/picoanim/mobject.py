from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class MObject:
    name: str | None = None
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0  # degrees
    opacity: float = 1.0   # 0..1
    visible: bool = True
    z: float = 0.0
    fill_color: object = "white"  # parsed later
    stroke_color: object = "black"
    stroke_width: int = 2
    # internal: scene ref set when added
    _scene: object | None = field(default=None, init=False, repr=False)

    def get_state(self) -> Dict[str, float]:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "scale": float(self.scale),
            "rotation": float(self.rotation),
            "opacity": float(self.opacity),
            "visible": bool(self.visible),
            "z": float(self.z),
        }

    def set_state(self, state: Dict[str, float]) -> None:
        for k, v in state.items():
            if hasattr(self, k):
                setattr(self, k, v)

    # Implemented by subclasses. Must return (tile_image, (offset_x, offset_y)) or draw directly.
    def _tile_and_offset(self, renderer):  # noqa: ANN001
        raise NotImplementedError
