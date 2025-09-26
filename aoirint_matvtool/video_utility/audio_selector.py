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


class AudioSelectorProgress(BaseModel):
    time: timedelta
    frame: int
    internal_time: timedelta
    internal_frame: int


class AudioSelector:
    def __init__(
        self,
        fps_parser: FpsParser,
        key_frame_parser: KeyFrameParser,
        ffmpeg_path: str,
    ) -> None:
        self._fps_parser = fps_parser
        self._key_frame_parser = key_frame_parser
        self._ffmpeg_path = ffmpeg_path

    async def select_audio(
        self,
        input_path: Path,
        audio_indexes: list[int],
        output_path: Path,
        progress_handler: (
            Callable[[AudioSelectorProgress], Awaitable[None]] | None
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

        audio_map_opts: list[str] = []
        for audio_index in audio_indexes:
            audio_map_opts.append("-map")
            audio_map_opts.append(f"0:a:{audio_index}")

        # Command Argument List
        command = [
            self._ffmpeg_path,
            "-hide_banner",
            "-n",  # fail if already exists
            "-i",
            str(input_path),
            "-map",
            "0:v:0",
            *audio_map_opts,
            "-map_metadata",
            "0",
            "-c",
            "copy",
            str(output_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
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
                        AudioSelectorProgress(
                            frame=progress.frame,
                            time=progress.time,
                            internal_frame=progress.internal_frame,
                            internal_time=progress.internal_time,
                        ),
                    )

        returncode = await wait_process(
            process=proc,
            stderr_handler=_handle_stderr,
        )
        if returncode != 0:
            raise Exception(f"FFmpeg errored. code: {returncode}")
