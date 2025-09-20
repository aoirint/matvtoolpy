import sys

from .base import ProgressHandler


class ProgressHandlerPlain(ProgressHandler):
    async def handle_progress(self, frame: int, time: str) -> None:
        print(
            f"Progress | Time {time}, frame {frame}",
            file=sys.stderr,
            flush=True,
        )
