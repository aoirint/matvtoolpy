import asyncio
import re
from collections.abc import Awaitable, Callable
from datetime import timedelta
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from ..progress_handler.utility.progress_calculator import ProgressCalculator
from ..util import exclude_none, parse_ffmpeg_time_unit_syntax
from ..utility.async_subprocess_helper import wait_process
from ..video_utility.fps_parser import FpsParser

logger = getLogger(__name__)


class CropScalerProgress(BaseModel):
    time: timedelta
    frame: int
    internal_time: timedelta
    internal_frame: int


class CropScaler:
    def __init__(
        self,
        fps_parser: FpsParser,
        ffmpeg_path: str,
    ) -> None:
        self._fps_parser = fps_parser
        self._ffmpeg_path = ffmpeg_path

    async def crop_scale(
        self,
        input_path: Path,
        crop: str | None,
        scale: str | None,
        video_codec: str | None,
        output_path: Path,
        progress_handler: (
            Callable[[CropScalerProgress], Awaitable[None]] | None
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

        # TODO: quality control
        if crop is not None and "," in crop:
            raise ValueError("Invalid crop argument. Remove ',' from crop.")

        if scale is not None and "," in scale:
            raise ValueError("Invalid scale argument. Remove ',' from scale.")

        crop_filter_string = f"crop={crop}" if crop is not None else None
        scale_filter_string = f"scale={scale}" if scale is not None else None

        video_filters = list(
            exclude_none(
                [
                    crop_filter_string,
                    scale_filter_string,
                ]
            )
        )
        video_filter_opts = (
            ["-filter:v", ",".join(video_filters)] if len(video_filters) != 0 else []
        )

        video_codec_opts = ["-c:v", video_codec] if video_codec is not None else []

        command = [
            self._ffmpeg_path,
            "-hide_banner",
            "-n",  # fail if already exists
            "-i",
            str(input_path),
            *video_filter_opts,
            *video_codec_opts,
            "-c:a",
            "copy",
            "-map",
            "0",
            "-map_metadata",
            "0",
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
                        CropScalerProgress(
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
