#!/usr/bin/env python3
"""
mad-rgb — unified RGB controller
Usage: python3 -m mad_rgb.main [effect]
Effects: aurora (default), breathing, rainbow, colorshift, starfield, fire, ripple, shootingstars
"""
import sys
import os
import time
sys.path.insert(0, os.path.expanduser("~"))

from mad_rgb.engine import RGBEngine
from mad_rgb.layout import load_layout, layout_key
from mad_rgb.devices.psu import ToughpowerIRGB
from mad_rgb.devices.openrgb_device import OpenRGBDevice
from mad_rgb.devices.razer_device import RAZER_NAMES, build_razer_devices
from mad_rgb.effects import ShootingStars, DeepOcean, Aurora, Breathing, ColorShift, RainbowWave, Starfield, Fire, Ripple

EFFECTS = {
    "aurora":        Aurora(speed=0.8),
    "breathing":     Breathing(color=(0, 100, 255), speed=0.8),
    "rainbow":       RainbowWave(speed=0.25),
    "colorshift":    ColorShift(speed=0.08),
    "starfield":     Starfield(density=0.5, speed=1.5),
    "fire":          Fire(speed=1.0, intensity=0.9),
    "ripple":        Ripple(speed=1.2, color=(0, 200, 255)),
    "shootingstars": ShootingStars(),
    "deepocean":     DeepOcean(),
}

effect_name = sys.argv[1] if len(sys.argv) > 1 else "aurora"
if effect_name not in EFFECTS:
    print(f"Unknown effect '{effect_name}'. Choose from: {', '.join(EFFECTS)}")
    sys.exit(1)


def build_devices():
    layout     = load_layout()
    devices    = []
    openrgb_ok = False

    # ── openrazer: direct kernel path for all Razer devices ──────────────────
    razer_devices = build_razer_devices(layout)
    devices.extend(razer_devices)

    # ── OpenRGB: non-Razer devices only (Corsair RAM, ASRock mobo, etc.) ─────
    seen: dict[str, int] = {}
    try:
        from openrgb import OpenRGBClient
        org = OpenRGBClient()
        for dev in org.devices:
            if dev.name in RAZER_NAMES:
                continue  # handled by openrazer
            key       = layout_key(dev.name, seen)
            positions = layout.get(key) or layout.get(dev.name)
            n         = len(dev.leds)
            if positions and len(positions) != n:
                print(f"  [warn] {key}: layout has {len(positions)} positions but device has {n} — ignoring layout")
                positions = None
            device = OpenRGBDevice(dev, [(p.x, p.y) for p in positions] if positions else None)
            devices.append(device)
            src = "layout" if positions else "strip"
            print(f"  OpenRGB [{src}]: {dev.name}  ({n} LEDs)")
        openrgb_ok = True
    except Exception as e:
        print(f"  OpenRGB unavailable: {e}")

    # ── HID: PSU direct ───────────────────────────────────────────────────────
    try:
        psu = ToughpowerIRGB()
        key = "Thermaltake Toughpower iRGB PLUS"
        positions = layout.get(key)
        if positions:
            psu.leds = positions
        devices.append(psu)
        src = "layout" if positions else "default ring"
        print(f"  HID [{src}]: {psu.name}  (12 LEDs)")
    except Exception as e:
        print(f"  PSU unavailable: {e}")

    return devices, openrgb_ok


RETRY_DELAY = 8

while True:
    print(f"\nEffect: {effect_name} — discovering devices…")
    devices, openrgb_ok = build_devices()

    if not devices:
        print(f"No devices found. Retrying in {RETRY_DELAY}s… (Ctrl+C to quit)")
        try:
            time.sleep(RETRY_DELAY)
        except KeyboardInterrupt:
            sys.exit(0)
        continue

    print(f"Running {len(devices)} device(s) at 120 fps.\n")
    effect = EFFECTS[effect_name]
    engine = RGBEngine(fps=120)
    for dev in devices:
        engine.assign(dev, effect)

    try:
        engine.run()
    except Exception as e:
        print(f"\nEngine crashed: {e} — reconnecting in {RETRY_DELAY}s…")
        try:
            time.sleep(RETRY_DELAY)
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        if not openrgb_ok:
            print(f"OpenRGB was not available at start. Retrying in {RETRY_DELAY}s…")
            try:
                time.sleep(RETRY_DELAY)
            except KeyboardInterrupt:
                sys.exit(0)
        else:
            sys.exit(0)
