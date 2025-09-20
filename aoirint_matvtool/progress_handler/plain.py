import sys
from datetime import timedelta

from ..util import format_timedelta_as_time_unit_syntax_string
from .base import ProgressHandler


class ProgressHandlerPlain(ProgressHandler):
    async def handle_progress(
        self,
        frame: int,
        time: timedelta,
        internal_frame: int,
        internal_time: timedelta,
    ) -> None:
        internal_time_string = format_timedelta_as_time_unit_syntax_string(
            td=internal_time,
        )

        time_string = format_timedelta_as_time_unit_syntax_string(
            td=time,
        )

        print(
            (
                f"Progress | Time {time_string}, "
                f"frame {frame} "
                f"(Internal time {internal_time_string}, "
                f"frame {internal_frame})"
            ),
            file=sys.stderr,
            flush=True,
        )
