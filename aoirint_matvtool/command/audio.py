from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..video_utility.audio_track_title_parser import AudioTrackTitleParser


async def execute_audio_cli(
    input_path: Path,
    ffprobe_path: str,
) -> None:
    title_parser = AudioTrackTitleParser(
        ffprobe_path=ffprobe_path,
    )

    titles = await title_parser.parse_titles(
        input_path=input_path,
    )

    for index, title in enumerate(titles):
        title = title or ""
        print(f"Audio Track {index}: {title}")


async def handle_audio_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    ffprobe_path: str = args.ffprobe_path

    input_path = Path(input_path_string)

    await execute_audio_cli(
        input_path=input_path,
        ffprobe_path=ffprobe_path,
    )


async def add_arguments_audio_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        help="Input video file path",
        required=True,
    )

    parser.set_defaults(handler=handle_audio_cli)
