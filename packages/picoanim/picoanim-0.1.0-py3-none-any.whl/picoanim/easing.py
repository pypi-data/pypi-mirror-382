import math
from typing import Callable


def linear(t: float) -> float:
    return max(0.0, min(1.0, float(t)))


def ease_in_out(t: float) -> float:
    t = linear(t)
    return 0.5 * (1 - math.cos(math.pi * t))


EASING: dict[str, Callable[[float], float]] = {
    "linear": linear,
    "ease_in_out": ease_in_out,
}
