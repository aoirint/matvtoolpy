import re
import subprocess
from collections.abc import Callable
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from .. import config
from ..util import exclude_none

logger = getLogger(__name__)


class CropScalerProgress(BaseModel):
    frame: int
    time: str


class CropScaler:
    def __init__(
        self,
        ffmpeg_path: str,
        ffprobe_path: str,
    ) -> None:
        self._ffmpeg_path = ffmpeg_path
        self._ffprobe_path = ffprobe_path

    def crop_scale(
        self,
        input_path: Path,
        crop: str | None,
        scale: str | None,
        video_codec: str | None,
        output_path: Path,
        progress_handler: Callable[[CropScalerProgress], None] | None = None,
    ) -> None:
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
            config.FFMPEG_PATH,
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
        proc = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )

        try:
            while proc.poll() is None:
                assert proc.stderr is not None
                line = proc.stderr.readline().strip()

                match = re.match(r"^frame=\ *(\d+?)\ .+time=(.+?)\ bitrate.+$", line)
                if match:
                    frame = int(match.group(1))
                    _time = match.group(2).strip()

                    if progress_handler:
                        progress_handler(
                            CropScalerProgress(
                                frame=frame,
                                time=_time,
                            ),
                        )

            returncode = proc.wait()
        finally:
            proc.kill()

        if returncode != 0:
            raise Exception(f"FFmpeg errored. code: {returncode}")
