from __future__ import annotations

from typing import Iterable, Tuple, Union

ColorLike = Union[str, Iterable[int]]


def _clamp8(v: float) -> int:
    return max(0, min(255, int(round(v))))


def parse_color(c: ColorLike) -> Tuple[int, int, int, int]:
    if c is None:
        return (0, 0, 0, 0)
    if isinstance(c, (tuple, list)):
        if len(c) == 3:
            r, g, b = c
            return (_clamp8(r), _clamp8(g), _clamp8(b), 255)
        if len(c) == 4:
            r, g, b, a = c
            return (_clamp8(r), _clamp8(g), _clamp8(b), _clamp8(a))
        raise ValueError("Tuple/list colors must have 3 or 4 elements")
    if isinstance(c, str):
        s = c.strip().lower()
        NAMED = {
            "black": (0, 0, 0, 255),
            "white": (255, 255, 255, 255),
            "red": (255, 0, 0, 255),
            "green": (0, 128, 0, 255),
            "blue": (0, 0, 255, 255),
            "transparent": (0, 0, 0, 0),
        }
        if s in NAMED:
            return NAMED[s]
        if s.startswith("#"):
            s = s[1:]
        if len(s) in (6, 8):
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            a = 255
            if len(s) == 8:
                a = int(s[6:8], 16)
            return (r, g, b, a)
        if s.startswith("rgb(") and s.endswith(")"):
            nums = [int(x) for x in s[4:-1].split(",")]
            if len(nums) != 3:
                raise ValueError("rgb() must have 3 numbers")
            return (_clamp8(nums[0]), _clamp8(nums[1]), _clamp8(nums[2]), 255)
        if s.startswith("rgba(") and s.endswith(")"):
            nums = [float(x) for x in s[5:-1].split(",")]
            if len(nums) != 4:
                raise ValueError("rgba() must have 4 numbers")
            r, g, b, a = nums
            return (_clamp8(r), _clamp8(g), _clamp8(b), _clamp8(a * 255))
    raise ValueError(f"Unsupported color format: {c}")


def apply_opacity(rgba: Tuple[int, int, int, int], opacity: float) -> Tuple[int, int, int, int]:
    r, g, b, a = rgba
    return (r, g, b, _clamp8(a * float(opacity)))
