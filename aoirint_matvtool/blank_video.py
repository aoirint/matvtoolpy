from pathlib import Path
from typing import Iterable, Optional, Union

from pydantic import BaseModel

from .find_image import FfmpegProgressLine


class FfmpegBlankVideoResult(BaseModel):
    success: bool
    message: Optional[str]


def ffmpeg_blank_video(
    input_path: Path,
    duration_seconds: Optional[str],
    output_path: Path,
) -> Iterable[Union[FfmpegBlankVideoResult, FfmpegProgressLine]]:
    raise Exception("WIP")
