import asyncio
from pathlib import Path

from pydantic import BaseModel


class _FfprobeStream(BaseModel):
    tags: dict[str, str] | None = None


class _FfprobeOutput(BaseModel):
    streams: list[_FfprobeStream]


class AudioTrackTitleParser:
    def __init__(
        self,
        ffprobe_path: str,
    ) -> None:
        self._ffprobe_path = ffprobe_path

    async def parse_titles(
        self,
        input_path: Path,
    ) -> list[str | None]:
        command = [
            self._ffprobe_path,
            "-hide_banner",
            "-i",
            str(input_path),
            "-show_streams",
            "-select_streams",
            "a",
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

        ret_titles: list[str | None] = []
        for stream in ffprobe_output.streams:
            title: str | None = None
            if stream.tags and "title" in stream.tags:
                title = stream.tags["title"]

            ret_titles.append(title)

        return ret_titles
