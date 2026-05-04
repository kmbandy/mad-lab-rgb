from .base import Device, LED


# Razer device names that openrazer handles — used to skip them in OpenRGB discovery
RAZER_NAMES: set[str] = set()


class RazerDevice(Device):
    """Direct-to-kernel LED control via openrazer advanced fx.

    Writes straight to the openrazer sysfs interface — no TCP hop,
    no OpenRGB server. Substantially lower latency than OpenRGBDevice
    for Razer hardware.
    """

    def __init__(self, org_device, led_positions: list[tuple[float, float]] | None = None):
        self._dev  = org_device
        self._adv  = org_device.fx.advanced
        self._rows = self._adv.rows
        self._cols = self._adv.cols
        self.name  = org_device.name
        n          = self._rows * self._cols

        if led_positions:
            self.leds = [LED(x=p[0], y=p[1]) for p in led_positions]
        else:
            self.leds = [LED(x=i / max(n - 1, 1), y=0.5) for i in range(n)]

        self.min_interval = 0.0  # direct kernel path, no artificial limit

    def send(self, colors: list[tuple[int, int, int]]) -> None:
        n = self._rows * self._cols
        for i, rgb in enumerate(colors[:n]):
            self._adv.matrix[i // self._cols, i % self._cols] = rgb
        self._adv.draw()

    def close(self) -> None:
        pass


def build_razer_devices(layout: dict) -> list["RazerDevice"]:
    """Discover all openrazer devices and populate RAZER_NAMES for OpenRGB exclusion."""
    global RAZER_NAMES
    devices: list[RazerDevice] = []

    try:
        import openrazer.client
        from mad_rgb.layout import layout_key
        dm   = openrazer.client.DeviceManager()
        seen: dict[str, int] = {}

        for dev in dm.devices:
            RAZER_NAMES.add(dev.name)
            key       = layout_key(dev.name, seen)
            positions = layout.get(key) or layout.get(dev.name)
            n         = dev.fx.advanced.rows * dev.fx.advanced.cols
            if positions and len(positions) != n:
                print(f"  [warn] {key}: layout has {len(positions)} positions but device has {n} — ignoring layout")
                positions = None
            device = RazerDevice(dev, [(p.x, p.y) for p in positions] if positions else None)
            devices.append(device)
            src = "layout" if positions else "strip"
            print(f"  openrazer [{src}]: {dev.name}  ({n} LEDs)")

    except Exception as e:
        print(f"  openrazer unavailable: {e}")

    return devices
