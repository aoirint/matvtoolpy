from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..inputs import ffmpeg_get_input


def execute_input_cli(
    input_path: Path,
) -> None:
    print(
        ffmpeg_get_input(
            input_path=input_path,
        )
    )


def handle_input_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    input_path = Path(input_path_string)

    execute_input_cli(
        input_path=input_path,
    )


def add_arguments_input_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )

    parser.set_defaults(handler=handle_input_cli)
