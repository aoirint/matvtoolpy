from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..key_frames import (
    ffmpeg_key_frames,
)


def execute_key_frames_cli(
    input_path: Path,
) -> None:
    for output in ffmpeg_key_frames(
        input_path=input_path,
    ):
        print(f"{output.time:.06f}")


def handle_key_frames_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    input_path = Path(input_path_string)

    execute_key_frames_cli(
        input_path=input_path,
    )


def add_arguments_key_frames_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )

    parser.set_defaults(handler=handle_key_frames_cli)
