import math
import random
import colorsys
from .base import Effect
from ..devices.base import LED


class ShootingStars(Effect):
    """
    Slow background hue rotation at low brightness + shooting stars flying
    across the canvas from random origin points in random directions.

    Stars have a white-hot head that fades to color along the tail.
    Trail width scales with speed so fast stars leave wider streaks.
    """

    def __init__(
        self,
        bg_speed:      float = 0.03,
        bg_brightness: float = 0.32,
        bg_saturation: float = 0.85,
        star_rate:     float = 2.0,    # stars per second
        star_speed:    float = 0.80,
        trail_width:   float = 0.07,
    ):
        self.bg_speed      = bg_speed
        self.bg_brightness = bg_brightness
        self.bg_saturation = bg_saturation
        self.star_rate     = star_rate
        self.star_speed    = star_speed
        self.trail_width   = trail_width
        self._stars: list[dict] = []
        self._next_spawn: float = 0.0

    def _make_star(self, t: float) -> dict:
        angle = random.uniform(0, 2 * math.pi)
        speed = self.star_speed * random.uniform(0.5, 1.8)
        return {
            "born":  t,
            "ox":    random.uniform(0.05, 0.95),   # random canvas origin
            "oy":    random.uniform(0.05, 0.95),
            "dx":    math.cos(angle),
            "dy":    math.sin(angle),
            "speed": speed,
            "hue":   random.random(),
            "life":  random.uniform(1.0, 2.2),
            "width": self.trail_width * (0.5 + 1.0 * (speed / self.star_speed)),
        }

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        if t >= self._next_spawn:
            self._stars.append(self._make_star(t))
            self._next_spawn = t + (1.0 / self.star_rate) * random.uniform(0.4, 1.6)

        self._stars = [s for s in self._stars if (t - s["born"]) < s["life"]]

        bg_hue = (t * self.bg_speed) % 1.0
        bg_r, bg_g, bg_b = colorsys.hsv_to_rgb(bg_hue, self.bg_saturation, self.bg_brightness)

        out = []
        for led in leds:
            r, g, b = bg_r, bg_g, bg_b

            for star in self._stars:
                age           = t - star["born"]
                dist_traveled = star["speed"] * age
                if dist_traveled <= 0:
                    continue

                # Vector from this star's origin to the LED
                lx   = led.x - star["ox"]
                ly   = led.y - star["oy"]
                proj = lx * star["dx"] + ly * star["dy"]

                if proj < 0 or proj > dist_traveled:
                    continue

                perp_x = lx - proj * star["dx"]
                perp_y = ly - proj * star["dy"]
                perp   = math.sqrt(perp_x * perp_x + perp_y * perp_y)
                if perp >= star["width"]:
                    continue

                along_t  = proj / dist_traveled
                perp_t   = 1.0 - (perp / star["width"]) ** 1.5
                tip_dist = dist_traveled - proj
                head_t   = max(0.0, 1.0 - tip_dist / (star["width"] * 2.5))
                life_t   = age / star["life"]
                life_fade = max(0.0, 1.0 - max(0.0, (life_t - 0.65) / 0.35))

                brightness = (along_t * 0.55 + head_t * 0.45) * perp_t * life_fade

                sr, sg, sb = colorsys.hsv_to_rgb(star["hue"], 1.0, 1.0)
                sr *= brightness
                sg *= brightness
                sb *= brightness

                r = min(1.0, r + sr)
                g = min(1.0, g + sg)
                b = min(1.0, b + sb)

            out.append((int(r * 255), int(g * 255), int(b * 255)))

        return out
