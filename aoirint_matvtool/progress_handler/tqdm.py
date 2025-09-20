from types import TracebackType
from typing import NoReturn, Self

from tqdm import tqdm

from .base import ProgressHandler


class ProgressHandlerTqdm(ProgressHandler):
    _tqdm_pbar: tqdm[NoReturn] | None

    def __init__(self) -> None:
        self._tqdm_pbar = None

    async def __aenter__(self) -> Self:
        self._tqdm_pbar = tqdm()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        if self._tqdm_pbar is not None:
            self._tqdm_pbar.close()
        return None

    async def handle_progress(self, frame: int, time: str) -> None:
        if self._tqdm_pbar is None:
            raise RuntimeError(
                "tqdm_pbar is not initialized. Did you forget to use 'with' statement?"
            )

        self._tqdm_pbar.set_postfix(
            {
                "time": time,
                "frame": f"{frame}",
            },
        )
        self._tqdm_pbar.refresh()
