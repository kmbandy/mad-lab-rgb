#!/usr/bin/env python3
"""
ASCII canvas preview of layout.json.
Usage: python3 -m mad_rgb.preview
"""
import sys
import os
sys.path.insert(0, os.path.expanduser("~"))

from mad_rgb.layout import load_layout

# Canvas dimensions
W = 80
H = 30

# Short labels for devices (truncated to fit)
LABELS = {
    "Corsair Vengeance Pro RGB 0":         "RAM0",
    "Corsair Vengeance Pro RGB 1":         "RAM1",
    "ASRock X570 Phantom Gaming-ITX/TB3":  "MOBO",
    "Razer Core X":                        "COREX",
    "Thermaltake Toughpower iRGB PLUS":    "PSU",
    "Razer Goliathus Extended":            "PAD",
    "Razer Ornata Chroma":                 "KBD",
    "Razer Mamba Elite":                   "MOUSE",
    "Razer Mouse Bungee V3 Chroma":        "BUNGEE",
    "Razer Base Station V2 Chroma":        "STAND",
}

# Color codes per device (cycles through a set)
COLORS = [
    "\033[92m",   # green
    "\033[93m",   # yellow
    "\033[94m",   # blue
    "\033[95m",   # magenta
    "\033[96m",   # cyan
    "\033[91m",   # red
    "\033[33m",   # dark yellow
    "\033[36m",   # dark cyan
    "\033[35m",   # dark magenta
    "\033[32m",   # dark green
]
RESET = "\033[0m"
DIM   = "\033[2m"


def main():
    import json
    from pathlib import Path

    layout_path = Path(__file__).parent / "layout.json"
    if not layout_path.exists():
        print("layout.json not found.")
        sys.exit(1)

    raw = json.loads(layout_path.read_text())
    zones = {k: v for k, v in raw.items() if not k.startswith("_")}
    layout = load_layout(layout_path)

    # Build grid: each cell is (char, color_code)
    grid = [["·" for _ in range(W)] for _ in range(H)]
    grid_color = [["" for _ in range(W)] for _ in range(H)]

    legend = []

    for idx, (name, leds) in enumerate(layout.items()):
        color = COLORS[idx % len(COLORS)]
        label = LABELS.get(name, name[:6].upper())
        legend.append((color, label, name, len(leds)))

        for i, led in enumerate(leds):
            cx = int(led.x * (W - 1))
            cy = int(led.y * (H - 1))
            cx = max(0, min(W - 1, cx))
            cy = max(0, min(H - 1, cy))
            # first LED of each device shows label char, rest show '●'
            char = label[i % len(label)] if i < len(label) else "●"
            grid[cy][cx] = char
            grid_color[cy][cx] = color

    # Draw border
    print()
    print(f"  {DIM}┌{'─' * W}┐{RESET}")
    for y, row in enumerate(grid):
        line = ""
        for x, ch in enumerate(row):
            c = grid_color[y][x]
            line += f"{c}{ch}{RESET}" if c else f"{DIM}{ch}{RESET}"
        # y-axis label every 5 rows
        y_label = f"{y/(H-1):.1f}" if y % 5 == 0 else "    "
        print(f"  {DIM}│{RESET}{line}{DIM}│{RESET} {DIM}{y_label}{RESET}")
    print(f"  {DIM}└{'─' * W}┘{RESET}")

    # x-axis tick marks
    ticks = "".join(
        f"{x/(W-1):.1f}"[1:] if x % 16 == 0 else " "
        for x in range(W)
    )
    print(f"   {DIM} {ticks}{RESET}")
    print()

    # Legend
    print("  Legend:")
    for color, label, name, n in legend:
        zone = zones.get(name, {})
        x, y = zone.get("x", "?"), zone.get("y", "?")
        w, h = zone.get("w", "?"), zone.get("h", "?")
        ori = zone.get("orientation", "horizontal")
        print(f"    {color}{label:8}{RESET}  {name}  ({n} leds)  "
              f"{DIM}x={x} y={y} w={w} h={h} [{ori}]{RESET}")
    print()


if __name__ == "__main__":
    main()
