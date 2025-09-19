import subprocess
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel


@dataclass
class StreamTitleExtractorStream:
    index: int
    codec_type: str
    title: str | None


class _FfprobeStream(BaseModel):
    index: int
    codec_type: str
    tags: dict[str, str] | None


class _FfprobeOutput(BaseModel):
    streams: list[_FfprobeStream]


class StreamTitleExtractor:
    def __init__(
        self,
        ffprobe_executable: str = "ffprobe",
    ) -> None:
        self.ffprobe_executable = ffprobe_executable

    def extract(self, input_file: Path) -> list[StreamTitleExtractorStream]:
        ffprobe_executable = self.ffprobe_executable

        command = [
            ffprobe_executable,
            "-hide_banner",
            "-i",
            str(input_file),
            "-print_format",
            "json",
            "-show_streams",
        ]
        proc = subprocess.run(command, stderr=subprocess.PIPE)
        stderr = proc.stderr.decode("utf-8")

        ffprobe_output = _FfprobeOutput.model_validate_json(stderr)

        ret_items: list[StreamTitleExtractorStream] = []
        for stream in ffprobe_output.streams:
            title: str | None = None
            if stream.tags and "title" in stream.tags:
                title = stream.tags["title"]

            ret_items.append(
                StreamTitleExtractorStream(
                    index=stream.index,
                    codec_type=stream.codec_type,
                    title=title,
                )
            )

        return ret_items
