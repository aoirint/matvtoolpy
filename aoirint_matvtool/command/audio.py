from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..inputs import ffmpeg_get_input


def execute_audio_cli(
    input_path: Path,
) -> None:
    inp = ffmpeg_get_input(
        input_path=input_path,
    )

    assert len(inp.streams) != 0
    stream = inp.streams[0]

    for track in stream.tracks:
        if track.type == "Audio":
            metadata_title = next(
                filter(
                    lambda metadata: metadata.key.lower() == "title", track.metadatas
                ),
                None,
            )
            title = metadata_title.value if metadata_title else ""

            print(f"Audio Track {track.index}: {title}")


def handle_audio_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path

    input_path = Path(input_path_string)

    execute_audio_cli(
        input_path=input_path,
    )


def add_arguments_audio_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        help="Input video file path",
        required=True,
    )

    parser.set_defaults(handler=handle_audio_cli)
