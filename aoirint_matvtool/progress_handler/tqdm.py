from types import TracebackType
from typing import TYPE_CHECKING, NoReturn, Self

from tqdm import tqdm

from .base import ProgressHandler

if TYPE_CHECKING:
    # NOTE: https://github.com/tqdm/tqdm/issues/1601
    TqdmNoReturn = tqdm[NoReturn]
else:
    TqdmNoReturn = tqdm


class ProgressHandlerTqdm(ProgressHandler):
    _tqdm_pbar: TqdmNoReturn | None

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
