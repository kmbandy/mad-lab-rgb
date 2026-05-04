import math
import random
from .base import Effect
from ..devices.base import LED


class Fire(Effect):
    """Heat rises from the bottom — warm glow effect."""

    def __init__(self, speed: float = 1.0, intensity: float = 1.0):
        self.speed     = speed
        self.intensity = intensity
        self._noise: dict[int, list[float]] = {}

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        out = []
        for i, led in enumerate(leds):
            # heat = distance from bottom (y=1 is hot base, y=0 cools off)
            heat_base = led.y
            # layered sine noise for flicker
            flicker = (
                math.sin(i * 1.7 + t * 5.0 * self.speed) * 0.3 +
                math.sin(i * 3.1 + t * 7.3 * self.speed) * 0.2 +
                math.sin(i * 0.9 + t * 3.1 * self.speed) * 0.15
            )
            heat = max(0.0, min(1.0, heat_base * self.intensity + flicker * 0.35))
            # heat → fire palette: black → red → orange → yellow → white
            if heat < 0.33:
                r = int(heat / 0.33 * 255)
                g, b = 0, 0
            elif heat < 0.66:
                r = 255
                g = int((heat - 0.33) / 0.33 * 160)
                b = 0
            else:
                r = 255
                g = int(160 + (heat - 0.66) / 0.34 * 95)
                b = int((heat - 0.66) / 0.34 * 200)
            out.append((r, g, b))
        return out
