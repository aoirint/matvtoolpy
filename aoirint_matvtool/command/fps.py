from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..fps import ffmpeg_fps


def execute_fps_cli(
    input_path: Path,
) -> None:
    print(
        ffmpeg_fps(
            input_path=input_path,
        ).fps
    )


def handle_fps_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    input_path = Path(input_path_string)

    execute_fps_cli(
        input_path=input_path,
    )


def add_arguments_fps_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )

    parser.set_defaults(handler=handle_fps_cli)
