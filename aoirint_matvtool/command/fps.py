from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..video_utility.fps_parser import FpsParser


async def execute_fps_cli(
    input_path: Path,
    ffprobe_path: str,
) -> None:
    fps_parser = FpsParser(
        ffprobe_path=ffprobe_path,
    )

    fps = await fps_parser.parse_fps(
        input_path=input_path,
    )
    print(fps)


async def handle_fps_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    ffprobe_path: str = args.ffprobe_path

    input_path = Path(input_path_string)

    await execute_fps_cli(
        input_path=input_path,
        ffprobe_path=ffprobe_path,
    )


async def add_arguments_fps_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )

    parser.set_defaults(handler=handle_fps_cli)
