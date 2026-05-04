import math
import colorsys
from .base import Effect
from ..devices.base import LED


class Ripple(Effect):
    """Concentric rings expand from the center of the LED layout."""

    def __init__(self, speed: float = 1.0, color: tuple[int,int,int] = (0, 180, 255),
                 rings: int = 3):
        self.speed = speed
        self.color = color
        self.rings = rings

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        out = []
        for led in leds:
            dist = math.sqrt((led.x - 0.5) ** 2 + (led.y - 0.5) ** 2) * 2  # 0-1
            wave = math.sin(dist * math.pi * self.rings - t * self.speed * math.pi * 2)
            bright = max(0.0, wave)
            out.append((
                int(self.color[0] * bright),
                int(self.color[1] * bright),
                int(self.color[2] * bright),
            ))
        return out
