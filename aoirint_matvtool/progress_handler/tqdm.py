from types import TracebackType
from typing import NoReturn, Self

from tqdm import tqdm

from .base import ProgressHandler


class ProgressHandlerTqdm(ProgressHandler):
    tqdm_pbar: tqdm[NoReturn] | None

    def __init__(self) -> None:
        self.tqdm_pbar = None

    def __enter__(self) -> Self:
        self.tqdm_pbar = tqdm()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        if self.tqdm_pbar is not None:
            self.tqdm_pbar.close()
        return None

    def handle_progress(self, frame: int, time: str) -> None:
        if self.tqdm_pbar is None:
            raise RuntimeError(
                "tqdm_pbar is not initialized. Did you forget to use 'with' statement?"
            )

        self.tqdm_pbar.set_postfix(
            {
                "time": time,
                "frame": f"{frame}",
            },
        )
        self.tqdm_pbar.refresh()
