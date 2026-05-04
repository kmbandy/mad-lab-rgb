from abc import ABC, abstractmethod
from ..devices.base import LED


class Effect(ABC):
    @abstractmethod
    def render(self, leds: list[LED], t: float) -> list[tuple[int, int, int]]:
        """t = elapsed seconds. Returns one (r,g,b) per LED."""
        ...
