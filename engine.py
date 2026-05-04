import time
import threading
from .devices.base import Device
from .effects.base import Effect


class _DeviceSender(threading.Thread):
    """Dedicated send thread for one device.

    The render loop calls push() every frame. The slot always holds the
    *latest* frame — if the device is still sending the previous one, the
    stale intermediate frame is silently overwritten. This keeps animation
    time advancing smoothly regardless of USB/TCP transfer latency.
    """

    def __init__(self, device: Device):
        super().__init__(daemon=True, name=f"sender/{device.name}")
        self._device  = device
        self._colors  = None
        self._lock    = threading.Lock()
        self._ready   = threading.Event()
        self._stop    = threading.Event()

    def push(self, colors: list[tuple[int, int, int]]) -> None:
        with self._lock:
            self._colors = colors
        self._ready.set()

    def stop(self) -> None:
        self._stop.set()
        self._ready.set()   # unblock a waiting thread

    def run(self) -> None:
        min_iv    = getattr(self._device, "min_interval", 0.0)
        last_send = -999.0

        while not self._stop.is_set():
            self._ready.wait()
            self._ready.clear()

            if self._stop.is_set():
                break

            # Honour per-device minimum send interval (e.g. I2C @ 83 ms)
            if min_iv:
                gap = min_iv - (time.perf_counter() - last_send)
                if gap > 0:
                    time.sleep(gap)

            with self._lock:
                colors = self._colors

            if colors is None:
                continue

            try:
                self._device.send(colors)
                last_send = time.perf_counter()
            except Exception as e:
                print(f"[{self._device.name}] send error: {e}")


class RGBEngine:
    def __init__(self, fps: float = 60.0):
        self.fps       = fps
        self._bindings: list[tuple[Device, Effect]] = []

    def assign(self, device: Device, effect: Effect) -> "RGBEngine":
        self._bindings.append((device, effect))
        return self

    def run(self) -> None:
        frame_time = 1.0 / self.fps

        # One dedicated sender thread per device
        senders: list[tuple[_DeviceSender, Device, Effect]] = []
        for device, effect in self._bindings:
            s = _DeviceSender(device)
            s.start()
            senders.append((s, device, effect))

        print(f"Running {len(self._bindings)} device(s) at {self.fps:.0f} fps target. Ctrl+C to stop.")

        start = time.perf_counter()
        frame = 0

        try:
            while True:
                t = time.perf_counter() - start

                for sender, device, effect in senders:
                    colors = effect.render(device.leds, t)
                    sender.push(colors)

                # Target absolute frame boundaries — prevents drift accumulation
                frame += 1
                sleep = (start + frame * frame_time) - time.perf_counter()
                if sleep > 0:
                    time.sleep(sleep)

        except KeyboardInterrupt:
            print("\nStopping — turning off LEDs.")
        finally:
            for sender, _, _ in senders:
                sender.stop()
            for sender, device, _ in senders:
                sender.join(timeout=2.0)
                try:
                    device.close()
                except Exception:
                    pass
