from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Self


@dataclass
class Progress:
    frame: int
    time: str


class ProgressHandler(ABC):
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        return None

    @abstractmethod
    def handle_progress(self, frame: int, time: str) -> None: ...
