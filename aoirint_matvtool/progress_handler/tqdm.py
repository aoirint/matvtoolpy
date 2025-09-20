from datetime import timedelta
from types import TracebackType
from typing import NoReturn, Self

from tqdm import tqdm

from ..util import format_timedelta_as_time_unit_syntax_string
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

    async def handle_progress(
        self,
        frame: int,
        time: timedelta,
        internal_frame: int,
        internal_time: timedelta,
    ) -> None:
        if self._tqdm_pbar is None:
            raise RuntimeError(
                "tqdm_pbar is not initialized. Did you forget to use 'with' statement?"
            )

        internal_time_string = format_timedelta_as_time_unit_syntax_string(
            td=internal_time,
        )

        time_string = format_timedelta_as_time_unit_syntax_string(
            td=time,
        )

        self._tqdm_pbar.set_postfix(
            {
                "time": time_string,
                "frame": f"{frame}",
                "internal_time": internal_time_string,
                "internal_frame": f"{internal_frame}",
            },
        )
        self._tqdm_pbar.refresh()

    async def clear(self) -> None:
        if self._tqdm_pbar is not None:
            self._tqdm_pbar.clear()
