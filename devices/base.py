from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LED:
    x: float = 0.0   # normalized 0-1
    y: float = 0.5


class Device(ABC):
    name: str = "unknown"
    leds: list[LED] = field(default_factory=list)

    @abstractmethod
    def send(self, colors: list[tuple[int, int, int]]) -> None: ...

    @abstractmethod
    def close(self) -> None: ...
