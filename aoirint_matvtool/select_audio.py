import re
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional, Union

from pydantic import BaseModel

from . import config
from .find_image import FfmpegProgressLine


class FfmpegSelectAudioResult(BaseModel):
    success: bool
    message: Optional[str]


def ffmpeg_select_audio(
    input_path: Path,
    audio_indexes: List[int],
    output_path: Path,
) -> Iterable[Union[FfmpegSelectAudioResult, FfmpegProgressLine]]:
    audio_map_options = []
    for audio_index in audio_indexes:
        audio_map_options.append("-map")
        audio_map_options.append(f"0:a:{audio_index}")

    command = [
        config.FFMPEG_PATH,
        "-hide_banner",
        "-n",  # fail if already exists
        "-i",
        str(input_path),
        "-map",
        "0:v:0",
        *audio_map_options,
        "-map_metadata",
        "0",
        "-c",
        "copy",
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

        message = "\n".join(lines[line_index:]) if line_index != len(lines) else None

        yield FfmpegSelectAudioResult(
            success=False,
            message=message,
        )
    else:
        yield FfmpegSelectAudioResult(
            success=True,
            message=None,
        )
