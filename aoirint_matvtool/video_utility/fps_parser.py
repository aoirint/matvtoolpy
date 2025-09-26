import asyncio
import re
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

logger = getLogger(__name__)


class _FfprobeStream(BaseModel):
    index: int
    avg_frame_rate: str | None = None


class _FfprobeOutput(BaseModel):
    streams: list[_FfprobeStream]


class FpsParser:
    def __init__(
        self,
        ffprobe_path: str,
    ) -> None:
        self._ffprobe_path = ffprobe_path

    async def parse_fps(
        self,
        input_path: Path,
    ) -> float:
        command = [
            self._ffprobe_path,
            "-hide_banner",
            "-i",
            str(input_path),
            "-show_streams",
            "-select_streams",
            "v",
            "-print_format",
            "json",
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout_bytes, _ = await proc.communicate()

        stdout = stdout_bytes.decode("utf-8")
        ffprobe_output = _FfprobeOutput.model_validate_json(stdout)

        if len(ffprobe_output.streams) == 0:
            raise Exception("No video stream found")

        first_video_stream = ffprobe_output.streams[0]
        if first_video_stream.avg_frame_rate is None:
            raise Exception("No avg_frame_rate found in the first video stream")

        match = re.match(r"^(\d+)/(\d+)$", first_video_stream.avg_frame_rate)
        if not match:
            raise Exception(
                f"Invalid avg_frame_rate format: {first_video_stream.avg_frame_rate}"
            )

        numerator = int(match.group(1))
        denominator = int(match.group(2))
        if denominator == 0:
            raise Exception("Denominator of avg_frame_rate is zero")

        fps = numerator / denominator
        return fps
