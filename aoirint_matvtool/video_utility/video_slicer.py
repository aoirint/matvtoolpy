import asyncio
import re
from collections.abc import Awaitable, Callable
from datetime import timedelta
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from ..progress_handler.utility.progress_calculator import (
    ProgressCalculator,
)
from ..util import (
    parse_ffmpeg_time_unit_syntax,
)
from ..utility.async_subprocess_helper import wait_process
from ..video_utility.fps_parser import FpsParser
from .key_frame_parser import KeyFrameParser

logger = getLogger(__name__)


class VideoSlicerProgress(BaseModel):
    time: timedelta
    frame: int
    internal_time: timedelta
    internal_frame: int


class VideoSlicer:
    def __init__(
        self,
        fps_parser: FpsParser,
        key_frame_parser: KeyFrameParser,
        ffmpeg_path: str,
    ) -> None:
        self._fps_parser = fps_parser
        self._key_frame_parser = key_frame_parser
        self._ffmpeg_path = ffmpeg_path

    async def slice_video(
        self,
        ss: str,
        to: str,
        input_path: Path,
        output_path: Path,
        progress_handler: (
            Callable[[VideoSlicerProgress], Awaitable[None]] | None
        ) = None,
    ) -> None:
        input_video_fps = await self._fps_parser.parse_fps(
            input_path=input_path,
        )

        progress_calculator = ProgressCalculator(
            start_timedelta=timedelta(),
            input_fps=input_video_fps,
            internal_fps=input_video_fps,
        )

        # Command Argument List
        command = [
            self._ffmpeg_path,
            "-hide_banner",
            "-n",  # fail if already exists
            "-ss",
            ss,
            "-to",
            to,
            "-i",
            str(input_path),
            "-map",
            "0",
            "-map_metadata",
            "0",
            "-c",
            "copy",
            str(output_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def _handle_stderr(line: str) -> None:
            match = re.match(r"^frame=\ *(\d+?)\ .+time=(.+?)\ bitrate.+$", line)
            if match:
                _frame = int(match.group(1))
                _time_string = match.group(2).strip()

                _time_struct = parse_ffmpeg_time_unit_syntax(_time_string)
                _time = _time_struct.to_timedelta()

                progress = progress_calculator.calculate_progress(
                    frame=_frame,
                    time=_time,
                )

                if progress_handler:
                    await progress_handler(
                        VideoSlicerProgress(
                            frame=progress.frame,
                            time=progress.time,
                            internal_frame=progress.internal_frame,
                            internal_time=progress.internal_time,
                        ),
                    )

        return_code = await wait_process(
            process=proc,
            stderr_handler=_handle_stderr,
        )
        if return_code != 0:
            raise Exception(f"FFmpeg errored. code: {return_code}")
