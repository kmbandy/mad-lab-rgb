import math
import random
import colorsys
from .base import Effect
from ..devices.base import LED


# ── Fish renderer ─────────────────────────────────────────────────────────────

def _render_fish(led_x: float, led_y: float, t: float) -> tuple[float, float, float] | None:
    """
    Returns an (r,g,b) float contribution if this LED is part of the fish,
    else None.  Fish swims back and forth in the keyboard zone.
    """
    # --- Swimming path ---
    cx = 0.51 + 0.21 * math.sin(t * 0.36)
    cy = 0.49 + 0.025 * math.sin(t * 0.71 + 1.0)

    # Velocity → swim direction
    vx = 0.21 * 0.36 * math.cos(t * 0.36)
    vy = 0.025 * 0.71 * math.cos(t * 0.71 + 1.0)
    spd = math.sqrt(vx * vx + vy * vy) or 1e-6
    dx = vx / spd          # unit vector pointing toward head
    dy = vy / spd
    turn = 1.0 if vx >= 0 else -1.0   # +1 = swimming right

    # --- Local fish coordinates ---
    rx = led_x - cx
    ry = led_y - cy
    u = rx * dx + ry * dy       # along body, + toward head
    v = -rx * dy + ry * dx      # perpendicular, + = "up" relative to fish

    HALF  = 0.090   # body half-length
    BW    = 0.048   # body half-width
    TAIL  = 0.055   # tail length behind body
    FIN_H = 0.030   # dorsal fin height

    # --- Body wiggle: traveling wave, zero at head, max at tail ---
    u_norm   = max(-1.0, min(1.0, u / HALF))
    tail_fac = max(0.0, -u_norm)              # 0 at head → 1 at tail
    phase    = 18.0 * u - 3.8 * t * turn
    wiggle   = 0.026 * tail_fac * math.sin(phase)
    vw       = v - wiggle                      # wiggle-adjusted lateral coord

    # --- Tail wiggle (extra phase offset so tail flicks further) ---
    tail_wiggle = 0.035 * math.sin(18.0 * u - 3.8 * t * turn + 0.7)
    vw_tail     = v - tail_wiggle

    # --- Body (filled ellipse) ---
    body_d = (u / HALF) ** 2 + (vw / BW) ** 2
    if body_d < 1.0:
        # Eye — small bright dot near head
        eu = HALF * 0.55
        ev = BW  * 0.28
        if (u - eu) ** 2 + (vw - ev) ** 2 < (0.010) ** 2:
            return (1.0, 1.0, 1.0)    # white eye

        # Body shading: brighter in center, soft edge
        edge  = max(0.0, 1.0 - body_d ** 0.6)
        bri   = 0.55 + 0.25 * edge
        # Subtle counter-shading: slightly lighter belly
        belly = max(0.0, -vw / BW) * 0.15
        r, g, b = colorsys.hsv_to_rgb(0.085, 0.92 - belly * 0.3, bri)
        return (r, g, b)

    # --- Dorsal fin (triangle above front half of body) ---
    fin_u0, fin_u1 = HALF * 0.05, HALF * 0.75
    if fin_u0 < u < fin_u1:
        fin_top = BW + FIN_H * (1.0 - (u - fin_u0) / (fin_u1 - fin_u0)) ** 0.7
        if BW - 0.005 < vw < fin_top:
            fin_bri = 0.45 * (1.0 - (u - fin_u0) / (fin_u1 - fin_u0))
            r, g, b = colorsys.hsv_to_rgb(0.075, 0.95, fin_bri)
            return (r, g, b)

    # --- Tail (caudal fin — forked chevron behind body) ---
    tail_u = -(u + HALF)           # 0 at back of body, TAIL at tip
    if 0.0 < tail_u < TAIL:
        t_prog  = tail_u / TAIL    # 0 near body → 1 at tip
        # Fork: two lobes, spread grows with tail_u
        spread  = BW * 1.5 * t_prog
        lobe_c  = BW * 0.6 * t_prog   # lobe centers move apart
        in_top  = abs(vw_tail - lobe_c)  < spread * (1.0 - t_prog * 0.3)
        in_bot  = abs(vw_tail + lobe_c)  < spread * (1.0 - t_prog * 0.3)
        if in_top or in_bot:
            bri = 0.40 * (1.0 - t_prog * 0.5)
            r, g, b = colorsys.hsv_to_rgb(0.08, 0.88, bri)
            return (r, g, b)

    return None


# ── Deep Ocean effect ─────────────────────────────────────────────────────────

class DeepOcean(Effect):
    """
    Bioluminescent deep-sea effect with an animated fish.

    Background: slow caustic undulation in deep blue/teal.
    Foreground: a fish swims back and forth across the keyboard zone,
                wiggling realistically, with dorsal fin, forked tail, and eye.
    Occasional soft glowing blobs drift through like distant jellyfish.
    """

    def __init__(
        self,
        base_hue:        float = 0.56,
        hue_drift:       float = 0.04,
        base_brightness: float = 0.16,
        wave_speed:      float = 0.18,
        wave_brightness: float = 0.11,
        blob_rate:       float = 0.20,
        min_floor:       float = 0.13,
    ):
        self.base_hue        = base_hue
        self.hue_drift       = hue_drift
        self.base_brightness = base_brightness
        self.wave_speed      = wave_speed
        self.wave_brightness = wave_brightness
        self.blob_rate       = blob_rate
        self.min_floor       = min_floor
        self._blobs: list[dict] = []
        self._next_blob: float  = random.uniform(2.0, 5.0)

    def _spawn_blob(self, t: float) -> dict:
        ox = random.uniform(0.05, 0.95)
        oy = random.uniform(0.08, 0.65)
        angle = random.uniform(0, 2 * math.pi)
        return {
            "born":  t,
            "ox":    ox, "oy":   oy,
            "dx":    math.cos(angle), "dy": math.sin(angle),
            "speed": random.uniform(0.03, 0.07),
            "curve": random.uniform(-0.3, 0.3),
            "hue":   self.base_hue + random.uniform(-0.12, 0.16),
            "size":  random.uniform(0.14, 0.24),
            "peak":  random.uniform(0.20, 0.32),
            "life":  random.uniform(6.0, 11.0),
        }

    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        # Spawn background blobs
        if t >= self._next_blob:
            self._blobs.append(self._spawn_blob(t))
            self._next_blob = t + (1.0 / self.blob_rate) * random.uniform(0.6, 1.4)
        self._blobs = [b for b in self._blobs if (t - b["born"]) < b["life"]]

        # Precompute blob positions
        blob_pos = []
        for b in self._blobs:
            age    = t - b["born"]
            angle  = b["curve"] * age
            ca, sa = math.cos(angle), math.sin(angle)
            rdx    = b["dx"] * ca - b["dy"] * sa
            rdy    = b["dx"] * sa + b["dy"] * ca
            bx     = b["ox"] + rdx * b["speed"] * age
            by_    = b["oy"] + rdy * b["speed"] * age
            life_t = age / b["life"]
            if   life_t < 0.15: env = life_t / 0.15
            elif life_t > 0.75: env = 1.0 - (life_t - 0.75) / 0.25
            else:               env = 1.0
            blob_pos.append((bx, by_, b["size"], b["peak"], b["hue"], env))

        out = []
        for led in leds:
            # ── Ocean background: caustic shimmer ────────────────────────────
            hue = self.base_hue + self.hue_drift * math.sin(t * 0.11 + led.x * 3.1)
            caustic = (
                math.sin(led.x * 7.3 + t * self.wave_speed) *
                math.sin(led.y * 5.1 + t * self.wave_speed * 0.7)
            )
            bri = self.base_brightness + self.wave_brightness * (caustic * 0.5 + 0.5)
            bri = max(self.min_floor, bri)
            r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 0.90, bri)

            # ── Background blobs (jellyfish glow) ────────────────────────────
            for bx, by_, size, peak, bhue, env in blob_pos:
                dx   = led.x - bx
                dy   = led.y - by_
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < size:
                    falloff = (1.0 - (dist / size) ** 1.8) * env
                    glow    = peak * falloff
                    cr, cg, cb = colorsys.hsv_to_rgb(bhue % 1.0, 0.70, glow)
                    r = min(1.0, r + cr)
                    g = min(1.0, g + cg)
                    b = min(1.0, b + cb)

            # ── Fish ─────────────────────────────────────────────────────────
            fish = _render_fish(led.x, led.y, t)
            if fish is not None:
                fr, fg, fb = fish
                # Blend fish over background (fish is opaque in body, additive at edges)
                r = min(1.0, r * 0.3 + fr)
                g = min(1.0, g * 0.3 + fg)
                b = min(1.0, b * 0.3 + fb)

            out.append((int(r * 255), int(g * 255), int(b * 255)))

        return out
