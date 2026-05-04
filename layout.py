"""
Loads layout.json and distributes LED positions within each device's bounding box.
Duplicate device names in OpenRGB are disambiguated with a " 0", " 1" suffix.
"""
import json
import math
from pathlib import Path
from .devices.base import LED

DEFAULT_LAYOUT_PATH = Path(__file__).parent / "layout.json"


def _distribute(n: int, x: float, y: float, w: float, h: float,
                orientation: str) -> list[LED]:
    if n == 0:
        return []
    if orientation == "ring":
        cx, cy = x + w / 2, y + h / 2
        rx, ry = w / 2, h / 2
        return [
            LED(
                x=cx + rx * math.cos(2 * math.pi * i / n - math.pi / 2),
                y=cy + ry * math.sin(2 * math.pi * i / n - math.pi / 2),
            )
            for i in range(n)
        ]
    if orientation == "vertical":
        return [LED(x=x + w / 2, y=y + (i / max(n - 1, 1)) * h) for i in range(n)]
    if orientation == "matrix":
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        return [
            LED(
                x=x + (i % cols) / max(cols - 1, 1) * w,
                y=y + (i // cols) / max(rows - 1, 1) * h,
            )
            for i in range(n)
        ]
    # horizontal (default)
    return [LED(x=x + (i / max(n - 1, 1)) * w, y=y + h / 2) for i in range(n)]


def load_layout(path: Path = DEFAULT_LAYOUT_PATH) -> dict[str, list[LED]]:
    """Returns {lookup_name: [LED, ...]}. Duplicate device names get ' 0', ' 1' suffixes."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {
        name: _distribute(
            n=int(zone.get("leds", 1)),
            x=float(zone.get("x", 0.0)),
            y=float(zone.get("y", 0.0)),
            w=float(zone.get("w", 0.1)),
            h=float(zone.get("h", 0.1)),
            orientation=zone.get("orientation", "horizontal"),
        )
        for name, zone in data.items()
        if not name.startswith("_")
    }


def layout_key(name: str, seen: dict[str, int]) -> str:
    """Return the disambiguated layout key for a device name.
    First occurrence → 'Name 0', second → 'Name 1', etc.
    If no duplicates exist in layout, just 'Name' is tried first.
    """
    idx = seen.get(name, 0)
    seen[name] = idx + 1
    return f"{name} {idx}"
