from __future__ import annotations

import math
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from .colors import apply_opacity, parse_color
from .mobject import MObject


class Circle(MObject):
    def __init__(self, radius: float = 50, fill: object = "white", stroke: object = "black", stroke_width: int = 2):
        super().__init__()
        self.radius = float(radius)
        self.fill_color = fill
        self.stroke_color = stroke
        self.stroke_width = int(stroke_width)

    def _tile_and_offset(self, renderer):  # noqa: ANN001
        r = max(0.0, self.radius * max(self.scale, 0.0))
        pad = max(2, int(self.stroke_width)) + 2
        size = int(math.ceil(2 * r)) + 2 * pad
        size = max(2, size)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = (pad, pad, size - pad, size - pad)
        fill = apply_opacity(parse_color(self.fill_color), self.opacity)
        outline = apply_opacity(parse_color(self.stroke_color), self.opacity)
        if fill[3] > 0:
            draw.ellipse(bbox, fill=fill)
        if self.stroke_width > 0 and outline[3] > 0:
            draw.ellipse(bbox, outline=outline, width=int(self.stroke_width))
        if abs(self.rotation) > 1e-6:
            img = img.rotate(-self.rotation, expand=True, resample=Image.BICUBIC)
        cx, cy = renderer.world_to_pixel(self.x, self.y)
        ox = int(round(cx - img.width / 2))
        oy = int(round(cy - img.height / 2))
        return img, (ox, oy)


class Rectangle(MObject):
    def __init__(self, width: float = 100, height: float = 60, fill: object = "white", stroke: object = "black", stroke_width: int = 2):
        super().__init__()
        self.width = float(width)
        self.height = float(height)
        self.fill_color = fill
        self.stroke_color = stroke
        self.stroke_width = int(stroke_width)

    def _tile_and_offset(self, renderer):  # noqa: ANN001
        w = max(1.0, self.width * max(self.scale, 0.0))
        h = max(1.0, self.height * max(self.scale, 0.0))
        pad = max(2, int(self.stroke_width)) + 2
        img_w = int(math.ceil(w)) + 2 * pad
        img_h = int(math.ceil(h)) + 2 * pad
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = (pad, pad, img_w - pad, img_h - pad)
        fill = apply_opacity(parse_color(self.fill_color), self.opacity)
        outline = apply_opacity(parse_color(self.stroke_color), self.opacity)
        if fill[3] > 0:
            draw.rectangle(bbox, fill=fill)
        if self.stroke_width > 0 and outline[3] > 0:
            draw.rectangle(bbox, outline=outline, width=int(self.stroke_width))
        if abs(self.rotation) > 1e-6:
            img = img.rotate(-self.rotation, expand=True, resample=Image.BICUBIC)
        cx, cy = renderer.world_to_pixel(self.x, self.y)
        ox = int(round(cx - img.width / 2))
        oy = int(round(cy - img.height / 2))
        return img, (ox, oy)


class Line(MObject):
    def __init__(self, start: Tuple[float, float] = (0, 0), end: Tuple[float, float] = (100, 0), stroke: object = "black", stroke_width: int = 2):
        super().__init__()
        self.start = (float(start[0]), float(start[1]))
        self.end = (float(end[0]), float(end[1]))
        self.stroke_color = stroke
        self.stroke_width = int(stroke_width)
        self.fill_color = "transparent"

    def _tile_and_offset(self, renderer):  # noqa: ANN001
        # Lines are drawn directly onto canvas; return None to signal direct draw.
        return None, (0, 0)

    def draw_direct(self, renderer, canvas):  # noqa: ANN001
        if not self.visible or self.opacity <= 0:
            return
        draw = ImageDraw.Draw(canvas)
        sx = self.x + self.start[0]
        sy = self.y + self.start[1]
        ex = self.x + self.end[0]
        ey = self.y + self.end[1]
        p1 = renderer.world_to_pixel(sx, sy)
        p2 = renderer.world_to_pixel(ex, ey)
        color = apply_opacity(parse_color(self.stroke_color), self.opacity)
        draw.line([p1, p2], fill=color, width=int(self.stroke_width))


class Text(MObject):
    def __init__(self, text: str, font_size: int = 32, color: object = "black", font: str | None = None):
        super().__init__()
        self.text = str(text)
        self.font_size = int(font_size)
        self.fill_color = color
        self.font_path = font

    def _get_font(self) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        try:
            if self.font_path:
                return ImageFont.truetype(self.font_path, self.font_size)
            # Try a common font; fallback to default
            try:
                return ImageFont.truetype("arial.ttf", self.font_size)
            except Exception:
                return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def _tile_and_offset(self, renderer):  # noqa: ANN001
        font = self._get_font()
        # Measure text
        tmp = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        bbox = d.textbbox((0, 0), self.text, font=font)
        w = max(1, int((bbox[2] - bbox[0]) * max(self.scale, 0.0)))
        h = max(1, int((bbox[3] - bbox[1]) * max(self.scale, 0.0)))
        pad = 4
        img = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(img)
        fill = apply_opacity(parse_color(self.fill_color), self.opacity)
        d2.text((pad, pad), self.text, font=font, fill=fill)
        if abs(self.rotation) > 1e-6:
            img = img.rotate(-self.rotation, expand=True, resample=Image.BICUBIC)
        cx, cy = renderer.world_to_pixel(self.x, self.y)
        ox = int(round(cx - img.width / 2))
        oy = int(round(cy - img.height / 2))
        return img, (ox, oy)
