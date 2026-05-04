import math
import colorsys
from .base import Effect
from ..devices.base import LED


class Breathing(Effect):
    """All LEDs pulse in and out on a single color."""

    def __init__(self, color: tuple[int,int,int] = (0, 100, 255), speed: float = 1.0):
        self.color = color
        self.speed = speed

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        bright = (math.sin(t * self.speed * math.pi) ** 2)
        r = int(self.color[0] * bright)
        g = int(self.color[1] * bright)
        b = int(self.color[2] * bright)
        return [(r, g, b)] * len(leds)
