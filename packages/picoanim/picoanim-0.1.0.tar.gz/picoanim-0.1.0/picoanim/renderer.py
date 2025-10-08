from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
from PIL import Image

from .mobject import MObject


class Renderer:
    def __init__(self, width: int = 640, height: int = 360, background: tuple[int, int, int, int] = (255, 255, 255, 255)):
        self.width = int(width)
        self.height = int(height)
        self.background = background

    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        # Origin at center, +x right, +y up
        px = int(round(self.width / 2 + x))
        py = int(round(self.height / 2 - y))
        return (px, py)

    def draw(self, mobjects: Iterable[MObject]) -> Image.Image:
        canvas = Image.new("RGBA", (self.width, self.height), self.background)
        # sort by z
        for m in sorted(mobjects, key=lambda m: m.z):
            if not m.visible or m.opacity <= 0:
                continue
            tile, offset = m._tile_and_offset(self)
            if tile is None:
                # must draw directly (e.g., Line)
                # provide the canvas to the object
                if hasattr(m, "draw_direct"):
                    m.draw_direct(self, canvas)
                continue
            canvas.alpha_composite(tile, dest=offset)
        return canvas

    def as_frame(self, img: Image.Image) -> np.ndarray:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        # Convert to RGB for broad writer compatibility (mp4/gif)
        img_rgb = img.convert("RGB")
        return np.asarray(img_rgb, dtype=np.uint8)
