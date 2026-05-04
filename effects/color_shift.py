import math
import colorsys
from .base import Effect
from ..devices.base import LED


class ColorShift(Effect):
    """Smooth hue rotation across the full spectrum — all LEDs in sync."""

    def __init__(self, speed: float = 0.1, saturation: float = 1.0):
        self.speed = speed
        self.saturation = saturation

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        hue = (t * self.speed) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, self.saturation, 1.0)
        c = (int(r * 255), int(g * 255), int(b * 255))
        return [c] * len(leds)


class RainbowWave(Effect):
    """Hue gradient that scrolls across LED positions."""

    def __init__(self, speed: float = 0.3, spread: float = 1.0):
        self.speed  = speed
        self.spread = spread

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        out = []
        for led in leds:
            hue = (led.x * self.spread + t * self.speed) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            out.append((int(r * 255), int(g * 255), int(b * 255)))
        return out
