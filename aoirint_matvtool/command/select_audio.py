import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from tqdm import tqdm

from ..find_image import (
    FfmpegProgressLine,
)
from ..select_audio import FfmpegSelectAudioResult, ffmpeg_select_audio


def execute_select_audio_cli(
    input_path: Path,
    audio_indexes: list[int],
    output_path: Path,
    progress_type: str,
) -> None:
    # tqdm
    tqdm_pbar = None
    if progress_type == "tqdm":
        tqdm_pbar = tqdm()

    try:
        for output in ffmpeg_select_audio(
            input_path=input_path,
            audio_indexes=audio_indexes,
            output_path=output_path,
        ):
            if isinstance(output, FfmpegProgressLine):
                if tqdm_pbar is not None:
                    tqdm_pbar.set_postfix(
                        {
                            "time": output.time,
                            "frame": f"{output.frame}",
                        }
                    )
                    tqdm_pbar.refresh()

                if progress_type == "plain":
                    print(
                        f"Progress | Time {output.time}, frame {output.frame}",
                        file=sys.stderr,
                    )

            if isinstance(output, FfmpegSelectAudioResult):
                if tqdm_pbar is not None:
                    tqdm_pbar.clear()

                print(f"Output | {output}")
    finally:
        if tqdm_pbar is not None:
            tqdm_pbar.close()


def handle_select_audio_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    audio_indexes: list[int] = args.audio_index
    output_path_string: str = args.output_path
    progress_type: str = args.progress_type

    input_path = Path(input_path_string)
    output_path = Path(output_path_string)

    execute_select_audio_cli(
        input_path=input_path,
        audio_indexes=audio_indexes,
        output_path=output_path,
        progress_type=progress_type,
    )


def add_arguments_select_audio_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )
    parser.add_argument(
        "--audio_index",
        type=int,
        nargs="+",
        required=True,
        help="Audio stream index(es) to select (0-based)",
    )
    parser.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=("tqdm", "plain", "none"),
        default="tqdm",
        help="Progress display type",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Output video file path",
    )
    parser.set_defaults(handler=handle_select_audio_cli)
