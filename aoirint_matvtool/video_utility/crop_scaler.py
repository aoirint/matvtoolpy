import re
import subprocess
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from .. import config
from ..find_image import FfmpegProgressLine
from ..util import exclude_none

logger = getLogger(__name__)


class FfmpegCropScaleResult(BaseModel):
    success: bool
    message: str | None


class CropScaler:
    def __init__(
        self,
        ffmpeg_path: str,
        ffprobe_path: str,
    ) -> None:
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def crop_scale(
        self,
        input_path: Path,
        crop: str | None,
        scale: str | None,
        video_codec: str | None,
        output_path: Path,
    ) -> Iterable[FfmpegCropScaleResult | FfmpegProgressLine]:
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

        lines = []
        try:
            while proc.poll() is None:
                assert proc.stderr is not None
                line = proc.stderr.readline().rstrip()
                lines += [line]

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
        finally:
            proc.kill()

        if returncode != 0:
            # skip Input or indented block to head the error message
            line_index = 0
            while line_index < len(lines):
                line = lines[line_index]
                match = re.search(r"^(Input|  ).+$", line)
                if not match:
                    break
                line_index += 1

            message = (
                "\n".join(lines[line_index:]) if line_index != len(lines) else None
            )

            yield FfmpegCropScaleResult(
                success=False,
                message=message,
            )
        else:
            yield FfmpegCropScaleResult(
                success=True,
                message=None,
            )
