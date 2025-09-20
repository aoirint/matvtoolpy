from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Self


@dataclass
class Progress:
    frame: int
    time: str


class ProgressHandler(ABC):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        return None

    @abstractmethod
    async def handle_progress(self, frame: int, time: str) -> None: ...
