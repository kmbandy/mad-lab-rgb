#!/usr/bin/env python3
"""
Connect to OpenRGB and print all devices + zones + LED counts.
Run this to figure out what to put in layout.json.
Usage: python3 -m mad_rgb.discover
"""
from openrgb import OpenRGBClient

def main():
    try:
        org = OpenRGBClient()
    except Exception as e:
        print(f"Could not connect to OpenRGB server: {e}")
        print("Start OpenRGB with: openrgb --server")
        return

    print(f"Found {len(org.devices)} device(s):\n")
    for i, dev in enumerate(org.devices):
        print(f"[{i}] \"{dev.name}\"")
        print(f"     type : {dev.type}")
        print(f"     leds : {len(dev.leds)} total")
        for j, zone in enumerate(dev.zones):
            print(f"     zone[{j}]: \"{zone.name}\"  ({len(zone.leds)} leds)")
        print()

    print("---")
    print("Copy device names into layout.json and assign x/y/w/h zones.")
    print("x, y = top-left corner (0-1). w, h = width/height (0-1).")
    print("orientation: horizontal | vertical | ring | matrix")

if __name__ == "__main__":
    main()
