from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..video_utility.fps_parser import FpsParser
from ..video_utility.key_frame_parser import (
    KeyFrameParser,
)


async def execute_key_frames_cli(
    input_path: Path,
    ffprobe_path: str,
) -> None:
    fps_parser = FpsParser(
        ffprobe_path=ffprobe_path,
    )

    key_frame_parser = KeyFrameParser(
        fps_parser=fps_parser,
        ffprobe_path=ffprobe_path,
    )

    key_frames = await key_frame_parser.parse_key_frames(
        input_path=input_path,
    )
    for key_frame in key_frames:
        print(f"{key_frame.total_seconds():.06f}")


async def handle_key_frames_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    ffprobe_path: str = args.ffprobe_path

    input_path = Path(input_path_string)

    await execute_key_frames_cli(
        input_path=input_path,
        ffprobe_path=ffprobe_path,
    )


async def add_arguments_key_frames_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )

    parser.set_defaults(handler=handle_key_frames_cli)
