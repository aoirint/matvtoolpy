import asyncio
from datetime import timedelta
from logging import getLogger
from pathlib import Path

from .fps_parser import FpsParser

logger = getLogger(__name__)


class KeyFrameParser:
    def __init__(
        self,
        fps_parser: FpsParser,
        ffprobe_path: str,
    ) -> None:
        self._fps_parser = fps_parser
        self._ffprobe_path = ffprobe_path

    async def parse_key_frame_times(
        self,
        input_path: Path,
    ) -> list[timedelta]:
        command = [
            self._ffprobe_path,
            "-hide_banner",
            "-skip_frame",
            "nokey",
            "-select_streams",
            "v",
            "-show_frames",
            "-show_entries",
            "frame=pkt_pts_time",
            "-of",
            "csv",
            str(input_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout_bytes, _ = await proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"FFprobe errored. code {proc.returncode}")

        stdout = stdout_bytes.decode("utf-8")

        stdout_lines = stdout.strip().splitlines()

        key_frame_times: list[timedelta] = []
        for line in stdout_lines:
            line = line.strip()
            if not line:
                continue

            # frame,0.007000
            # frame,0.007000,side_data,H.26[45] User Data Unregistered SEI message
            # frame,0.007000side_data,H.26[45] User Data Unregistered SEI message
            row = line.split(",")
            if len(row) < 2:
                continue

            if row[0] != "frame":
                continue

            seconds_string = row[1].strip()

            # Workaround for FFprobe issue: (side_data.+)?
            # https://trac.ffmpeg.org/ticket/7153
            # Correct: frame,0.007000,side_data,H.26[45] User Data Unregistered SEI message  # noqa: E501
            # Broken: frame,0.007000side_data,H.26[45] User Data Unregistered SEI message  # noqa: E501
            if seconds_string.endswith("side_data"):
                seconds_string = seconds_string[:-9]  # 0.007000side_data -> 0.007000

            seconds = float(seconds_string)

            time = timedelta(seconds=seconds)
            key_frame_times.append(time)

        return key_frame_times
