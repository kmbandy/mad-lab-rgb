from openrgb.utils import RGBColor
from .base import Device, LED

# Devices known to use I2C/SMBus — hardware caps at ~12fps (83ms per call)
_I2C_NAMES = ("Corsair", "ASRock", "Gigabyte", "ASUS Aura", "MSI Mystic")


def _best_mode(dev):
    """Return (mode_index, is_per_led) for the best color-accepting mode."""
    mode_names = [m.name for m in dev.modes]
    if "Direct" in mode_names:
        return mode_names.index("Direct"), True
    if "Static" in mode_names:
        return mode_names.index("Static"), False
    if "Custom" in mode_names:
        return mode_names.index("Custom"), True
    return None, False


class OpenRGBDevice(Device):
    def __init__(self, org_device, led_positions: list[tuple[float, float]] | None = None):
        self._dev = org_device
        self.name = org_device.name
        n         = len(org_device.leds)

        if led_positions:
            self.leds = [LED(x=p[0], y=p[1]) for p in led_positions]
        else:
            self.leds = [LED(x=i / max(n - 1, 1), y=0.5) for i in range(n)]

        mode_idx, self._per_led = _best_mode(org_device)
        if mode_idx is not None and org_device.active_mode != mode_idx:
            try:
                org_device.set_mode(mode_idx)
            except Exception:
                pass

        # I2C devices have an 83ms hardware poll cycle — tell the engine not to
        # queue another send until the previous one finishes
        self.min_interval = 0.080 if any(k in self.name for k in _I2C_NAMES) else 0.0

    def send(self, colors: list[tuple[int, int, int]]) -> None:
        if self._per_led:
            self._dev.set_colors([RGBColor(*c) for c in colors])
        else:
            mid = colors[len(colors) // 2]
            self._dev.set_colors([RGBColor(*mid)] * len(colors))

    def close(self):
        pass
