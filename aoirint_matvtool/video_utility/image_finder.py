import asyncio
import re
from collections.abc import Awaitable, Callable
from datetime import timedelta
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from aoirint_matvtool.fps import ffmpeg_fps
from aoirint_matvtool.progress_handler.utility.progress_calculator import (
    ProgressCalculator,
)

from ..util import exclude_none, parse_ffmpeg_time_unit_syntax
from ..utility.async_subprocess_helper import wait_process

logger = getLogger(__name__)


class ImageFinderProgress(BaseModel):
    time: timedelta
    frame: int
    internal_time: timedelta
    internal_frame: int


class ImageFinderResult(BaseModel):
    frame: int
    pblack: int
    pts: int
    t: float
    type: str
    last_keyframe: int


class ImageFinder:
    def __init__(
        self,
        ffmpeg_path: str,
    ) -> None:
        self._ffmpeg_path = ffmpeg_path

    async def find_image(
        self,
        input_video_ss: str | None,
        input_video_to: str | None,
        input_video_path: Path,
        input_video_crop: str | None,
        reference_image_path: Path,
        reference_image_crop: str | None,
        fps: int | None,
        blackframe_amount: int = 98,
        blackframe_threshold: int = 32,
        progress_handler: Callable[[ImageFinderProgress], Awaitable[None]]
        | None = None,
        result_handler: Callable[[ImageFinderResult], Awaitable[None]] | None = None,
    ) -> None:
        # FPS
        # TODO: モジュール化
        input_video_fps = ffmpeg_fps(input_path=input_video_path).fps
        if not input_video_fps:
            raise Exception("Failed to get FPS info from the input video.")

        progress_calculator = ProgressCalculator(
            start_timedelta=timedelta(),
            input_fps=input_video_fps,
            internal_fps=input_video_fps,
        )

        # Create the input video filter_complex string
        input_video_filter_fps = f"fps={fps}" if fps is not None else None
        input_video_filter_crop = (
            f"crop={input_video_crop}" if input_video_crop is not None else None
        )

        input_video_filters = list(
            exclude_none(
                [
                    input_video_filter_fps,
                    input_video_filter_crop,
                ]
            )
        )

        input_video_filter_complex: str | None = None
        if len(input_video_filters) != 0:
            input_video_filter_inner_string = ",".join(input_video_filters)
            input_video_filter_complex = f"[0:v]{input_video_filter_inner_string}[va]"

        # Create the reference image filter_complex string
        reference_image_filter_fps = f"fps={fps}" if fps is not None else None
        reference_image_filter_crop = (
            f"crop={reference_image_crop}" if reference_image_crop is not None else None
        )

        reference_image_filters = list(
            exclude_none(
                [
                    reference_image_filter_fps,
                    reference_image_filter_crop,
                ]
            )
        )

        reference_image_filter_complex: str | None = None
        if len(reference_image_filters) != 0:
            reference_image_filter_inner_string = ",".join(reference_image_filters)
            reference_image_filter_complex = (
                f"[1:v]{reference_image_filter_inner_string}[vb]"
            )

        # Create the blend filter_complex string
        blend_filter_complex_inner_string = f"blend=difference:shortest=1,blackframe=amount={blackframe_amount}:threshold={blackframe_threshold}"  # noqa: E501
        blend_input_a_name = "va" if input_video_filter_complex is not None else "0:v"
        blend_input_b_name = "vb" if input_video_filter_complex is not None else "1:v"

        blend_filter_complex = f"[{blend_input_a_name}][{blend_input_b_name}]{blend_filter_complex_inner_string}"  # noqa: E501

        # Create the filter_complex string
        filter_complex_filters = list(
            exclude_none(
                [
                    input_video_filter_complex,
                    reference_image_filter_complex,
                    blend_filter_complex,
                ]
            )
        )
        filter_complex = ";".join(filter_complex_filters)

        slice_opts: list[str] = []
        if input_video_ss is not None:
            slice_opts += [
                "-ss",
                input_video_ss,
            ]

        if input_video_to is not None:
            slice_opts += [
                "-to",
                input_video_to,
            ]

        # Command Argument List
        command = [
            self._ffmpeg_path,
            "-hide_banner",
            *slice_opts,
            "-i",
            str(input_video_path),
            "-loop",
            "1",
            "-i",
            str(reference_image_path),
            "-an",
            "-filter_complex",
            filter_complex,
            "-f",
            "null",
            "-",
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def _handle_stderr(line: str) -> None:
            match = re.match(r"^\[Parsed_blackframe.+?\]\ (frame:.+)$", line)
            if (
                match
            ):  # "frame:810 pblack:99 pts:13516 t:13.516000 type:P last_keyframe:720"
                result = match.group(1).strip()

                result_dict: dict[str, str] = {}
                for key_value in result.split(" "):
                    key, value = key_value.split(":", maxsplit=2)
                    result_dict[key] = value

                if result_handler:
                    await result_handler(
                        ImageFinderResult.model_validate(result_dict),
                    )

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
                        ImageFinderProgress(
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
