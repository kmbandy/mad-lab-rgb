import math
import hid
from .base import Device, LED

VENDOR_ID  = 0x264A
PRODUCT_ID = 0x2329
NUM_LEDS   = 12


class ToughpowerIRGB(Device):
    name = "Thermaltake Toughpower iRGB PLUS"

    def __init__(self):
        self._dev = hid.device()
        self._dev.open(VENDOR_ID, PRODUCT_ID)
        self._dev.set_nonblocking(1)
        # 12 LEDs arranged in a ring — positions on unit circle
        self.leds = [
            LED(
                x=0.5 + 0.5 * math.cos(2 * math.pi * i / NUM_LEDS - math.pi / 2),
                y=0.5 + 0.5 * math.sin(2 * math.pi * i / NUM_LEDS - math.pi / 2),
            )
            for i in range(NUM_LEDS)
        ]
        self.min_interval = 0.033  # ~30 fps; prevents HID queue flooding
        self._init()

    def _init(self):
        buf = [0x00, 0xFE, 0x31] + [0x00] * 62
        self._dev.write(buf)

    def send(self, colors: list[tuple[int, int, int]]) -> None:
        payload = [0x00, 0x30, 0x42, 0x18, 0x00]
        for r, g, b in colors[:NUM_LEDS]:
            payload += [r, b, g]  # PSU uses RBG ordering
        payload += [0x00] * (65 - len(payload))
        self._dev.write(payload[:65])

    def close(self):
        self.send([(0, 0, 0)] * NUM_LEDS)
        self._dev.close()
