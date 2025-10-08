from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path


class Handler(ABC):
    suffix: str
    template: str
    renderer: str

    @staticmethod
    @abstractmethod
    def detect(source_path: Path) -> bool:
        """Return True to indicate that the handler should process the given source file."""
        pass


handlers: list[Any] = []


def handler():
    def decorator(extension):
        # global handlers
        handlers.append(extension)
        return extension
    return decorator
