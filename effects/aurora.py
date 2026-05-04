import math
import colorsys
from .base import Effect
from ..devices.base import LED


class Aurora(Effect):
    """Layered sine waves — greens/teals/purples drifting like a real aurora."""

    def __init__(self, speed: float = 0.8, scale: float = 1.0):
        self.speed = speed
        self.scale = scale

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        out = []
        for led in leds:
            w1 = math.sin(led.x * 6.0 * self.scale + t * self.speed)
            w2 = math.sin(led.y * 4.0 * self.scale + t * self.speed * 0.7 + 1.2)
            w3 = math.sin((led.x + led.y) * 3.0 * self.scale - t * self.speed * 0.5)
            v = (w1 + w2 + w3) / 3.0
            hue = (0.45 + v * 0.15 + t * 0.015 * self.speed) % 1.0
            bright = max(0.0, 0.5 + v * 0.45)
            r, g, b = colorsys.hsv_to_rgb(hue, 0.85, bright)
            out.append((int(r * 255), int(g * 255), int(b * 255)))
        return out
