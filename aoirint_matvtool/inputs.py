import re
import subprocess
from pathlib import Path
from typing import List

from pydantic import BaseModel

from . import config
from .config import logger


class FfmpegMetadataItem(BaseModel):
    key: str
    value: str


class FfmpegTrack(BaseModel):
    index: int
    type: str
    text: str
    metadatas: List[FfmpegMetadataItem]


class FfmpegStream(BaseModel):
    index: int
    tracks: List[FfmpegTrack]


class FfmpegInput(BaseModel):
    index: int
    text: str
    streams: List[FfmpegStream]
    metadatas: List[FfmpegMetadataItem]


def __find_all_input_line_index(lines: List[str]) -> List[int]:
    indexes: List[int] = []

    for line_index, line in enumerate(lines):
        match = re.search(r"^Input #.+$", line)
        if match:
            indexes.append(line_index)

    return indexes


def __find_all_stream_line_index(lines: List[str]) -> List[int]:
    indexes: List[int] = []

    for line_index, line in enumerate(lines):
        # FFmpeg 4.2: indent level 4
        # FFmpeg 4.4: indent level 2
        match = re.search(r"^(?:\s{2}|\s{4})Stream #.+$", line)
        if match:
            indexes.append(line_index)

    return indexes


def __find_all_metadata_line_index(lines: List[str], level: int) -> List[int]:
    indent = " " * level

    indexes: List[int] = []

    for line_index, line in enumerate(lines):
        match = re.search(r"^" + indent + r"Metadata:", line)
        if match:
            indexes.append(line_index)

    return indexes


def __read_first_metadata_items(
    lines: List[str], level: int
) -> List[FfmpegMetadataItem]:
    metadata_line_indexes = __find_all_metadata_line_index(lines=lines, level=level)
    assert len(metadata_line_indexes) != 0

    indent = " " * (level + 2)

    metadatas: List[FfmpegMetadataItem] = []

    metadata_line_index = metadata_line_indexes[0]
    metadata_line_index_end = len(lines)
    metadata_lines = lines[metadata_line_index:metadata_line_index_end]
    for metadata_line in metadata_lines:
        match_metadata_item = re.search(r"^" + indent + r"(.+?):(.+)$", metadata_line)
        if not match_metadata_item:
            continue

        metadata_key = match_metadata_item.group(1).strip()
        metadata_value = match_metadata_item.group(2).strip()
        metadatas.append(FfmpegMetadataItem(key=metadata_key, value=metadata_value))

    return metadatas


# API
def ffmpeg_get_input(input_path: Path) -> FfmpegInput:
    command = [
        config.FFMPEG_PATH,
        "-hide_banner",
        "-i",
        str(input_path),
    ]
    proc = subprocess.run(command, stderr=subprocess.PIPE)
    stderr = proc.stderr.decode("utf-8")

    lines = stderr.splitlines()

    inputs: List[FfmpegInput] = []

    input_line_indexes = __find_all_input_line_index(lines=lines)
    for input_index, input_line_index in enumerate(input_line_indexes):
        input_line_index_end = (
            input_line_indexes[input_index + 1]
            if input_index + 1 != len(input_line_indexes)
            else len(lines)
        )

        input_line_header = lines[input_line_index]
        match_input = re.search(r"^Input #(\d+?), (.+)$", input_line_header)
        if not match_input:
            continue

        input_header_index = int(match_input.group(1))
        input_header_text = match_input.group(2)
        logger.debug(f"Input {input_header_index} {input_header_text}")

        input_lines = lines[input_line_index + 1 : input_line_index_end]
        stream_line_indexes = __find_all_stream_line_index(lines=input_lines)

        input_metadata_lines = input_lines[0 : stream_line_indexes[0]]
        input_metadatas = __read_first_metadata_items(
            lines=input_metadata_lines, level=2
        )
        logger.debug(f"Input Metadatas {input_metadatas}")

        streams: List[FfmpegStream] = []

        for stream_index, stream_line_index in enumerate(stream_line_indexes):
            stream_line_index_end = (
                stream_line_indexes[stream_index + 1]
                if stream_index + 1 != len(stream_line_indexes)
                else len(input_lines)
            )

            stream_line_header = input_lines[stream_line_index]

            # FFmpeg 4.2: indent level 4
            # FFmpeg 4.4: indent level 2
            match_stream = re.search(
                r"^(?:\s{2}|\s{4})Stream #(\d+?):(\d+?).*?: (Video|Audio): (.+)$",
                stream_line_header,
            )
            if not match_stream:
                continue

            stream_header_index = int(match_stream.group(1))
            stream_track_index = int(match_stream.group(2))
            stream_type = match_stream.group(3)
            stream_text = match_stream.group(4)
            logger.debug(
                f"Stream Track {stream_index} {stream_track_index} {stream_type} {stream_text}"
            )

            stream_lines = input_lines[stream_line_index + 1 : stream_line_index_end]
            track_metadatas = __read_first_metadata_items(lines=stream_lines, level=4)
            logger.debug(f"Stream Track Metadatas {track_metadatas}")

            stream = next(
                filter(lambda stream: stream.index == stream_header_index, streams),
                None,
            )
            track = FfmpegTrack(
                index=stream_track_index,
                type=stream_type,
                text=stream_text,
                metadatas=track_metadatas,
            )
            if stream is None:
                stream = FfmpegStream(
                    index=stream_header_index,
                    tracks=[],
                )
                streams.append(stream)

            stream.tracks.append(track)

        inputs.append(
            FfmpegInput(
                index=input_header_index,
                text=input_header_text,
                streams=streams,
                metadatas=input_metadatas,
            )
        )

    if len(inputs) == 0:
        raise Exception(f"File not found: {input_path}")

    return inputs[0]
