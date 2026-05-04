import math
import random
import colorsys
from .base import Effect
from ..devices.base import LED


class Starfield(Effect):
    """Random LEDs twinkle in and out like stars."""

    def __init__(self, density: float = 0.4, speed: float = 1.5,
                 color: tuple[int,int,int] | None = None):
        self.density = density
        self.speed   = speed
        self.color   = color  # None = random hues per star
        self._stars: dict[int, dict] = {}

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        out = [(0, 0, 0)] * len(leds)
        # spawn new stars
        for i in range(len(leds)):
            if i not in self._stars and random.random() < self.density * 0.05:
                self._stars[i] = {
                    "born": t,
                    "life": random.uniform(0.4, 1.2) / self.speed,
                    "hue":  random.random() if self.color is None else None,
                }
        # render and reap
        dead = []
        for i, star in self._stars.items():
            age  = (t - star["born"]) / star["life"]
            if age >= 1.0:
                dead.append(i)
                continue
            # triangle envelope: ramp up then down
            bright = 1.0 - abs(age * 2 - 1)
            if self.color:
                r = int(self.color[0] * bright)
                g = int(self.color[1] * bright)
                b = int(self.color[2] * bright)
            else:
                r, g, b = colorsys.hsv_to_rgb(star["hue"], 0.6, bright)
                r, g, b = int(r*255), int(g*255), int(b*255)
            if i < len(out):
                out[i] = (r, g, b)
        for i in dead:
            del self._stars[i]
        return out
