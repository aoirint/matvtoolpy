import re
import subprocess
from pathlib import Path
from typing import Generator, Optional, Union

from pydantic import BaseModel

from . import config
from .util import exclude_none


class FfmpegBlackframeOutputLine(BaseModel):
    frame: int
    pblack: int
    pts: int
    t: float
    type: str
    last_keyframe: int


class FfmpegProgressLine(BaseModel):
    frame: int
    time: str


def ffmpeg_find_image_generator(
    input_video_ss: Optional[str],
    input_video_to: Optional[str],
    input_video_path: Path,
    input_video_crop: Optional[str],
    reference_image_path: Path,
    reference_image_crop: Optional[str],
    fps: Optional[int],
    blackframe_amount: int = 98,
    blackframe_threshold: int = 32,
) -> Generator[Union[FfmpegBlackframeOutputLine, FfmpegProgressLine], None, None]:
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

    input_video_filter_complex: Optional[str] = None
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

    reference_image_filter_complex: Optional[str] = None
    if len(reference_image_filters) != 0:
        reference_image_filter_inner_string = ",".join(reference_image_filters)
        reference_image_filter_complex = (
            f"[1:v]{reference_image_filter_inner_string}[vb]"
        )

    # Create the blend filter_complex string
    blend_filter_complex_inner_string = f"blend=difference:shortest=1,blackframe=amount={blackframe_amount}:threshold={blackframe_threshold}"  # noqa: B950
    blend_input_a_name = "va" if input_video_filter_complex is not None else "0:v"
    blend_input_b_name = "vb" if input_video_filter_complex is not None else "1:v"

    blend_filter_complex = f"[{blend_input_a_name}][{blend_input_b_name}]{blend_filter_complex_inner_string}"  # noqa: B950

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

    slice_opts = []
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
        config.FFMPEG_PATH,
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
    proc = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    try:
        while proc.poll() is None:
            assert proc.stderr is not None
            line = proc.stderr.readline().rstrip()

            match = re.match(r"^\[Parsed_blackframe.+?\]\ (frame:.+)$", line)
            if (
                match
            ):  # "frame:810 pblack:99 pts:13516 t:13.516000 type:P last_keyframe:720"
                result = match.group(1).strip()

                result_dict = {}
                for key_value in result.split(" "):
                    key, value = key_value.split(":", maxsplit=2)
                    result_dict[key] = value

                output = FfmpegBlackframeOutputLine.parse_obj(result_dict)
                yield output

            match = re.match(r"^frame=\ *(\d+?)\ .+time=(.+?)\ bitrate.+$", line)
            if match:
                frame = int(match.group(1))
                _time = match.group(2).strip()

                progress = FfmpegProgressLine(
                    frame=frame,
                    time=_time,
                )
                yield progress

        returncode = proc.wait()
        if returncode != 0:
            raise Exception(f"FFmpeg errored. code {returncode}")
    finally:
        proc.kill()
