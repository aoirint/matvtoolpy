import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from .inputs import ffmpeg_get_input
from .util import integer_part_and_decimal_part_to_float


class FfmpegFpsResult(BaseModel):
    success: bool
    fps: Optional[float]


def ffmpeg_fps(input_path: Path) -> FfmpegFpsResult:
    input_video = ffmpeg_get_input(input_path=input_path)

    input_video_track = next(
        filter(lambda track: track.type == "Video", input_video.streams[0].tracks)
    )
    # h264 (High), yuv420p(tv, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 60 fps, 60 tbr, 1k tbn, 120 tbc (default)  # noqa: B950
    input_video_track_text = input_video_track.text
    match = re.search(r"(\d+)(\.\d+)?\ fps", input_video_track_text)

    if match:
        input_video_fps_integer_part = int(match.group(1))
        input_video_fps_decimal_part = (
            int(match.group(2)[1:]) if match.group(2) is not None else 0
        )  # maybe None

        input_video_fps = integer_part_and_decimal_part_to_float(
            integer_part=input_video_fps_integer_part,
            decimal_part=input_video_fps_decimal_part,
        )

        return FfmpegFpsResult(
            success=True,
            fps=float(input_video_fps),
        )

    return FfmpegFpsResult(
        success=False,
        fps=None,
    )
