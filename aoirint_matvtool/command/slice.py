import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Literal, TypeGuard

from tqdm import tqdm

from ..slice import FfmpegProgressLine, FfmpegSliceResult, ffmpeg_slice


def validate_progress_type(value: Any) -> TypeGuard[Literal["tqdm", "plain", "none"]]:
    return value in ("tqdm", "plain", "none")


def execute_slice_cli(
    ss: str,
    to: str,
    input_path: Path,
    output_path: Path,
    progress_type: Literal["tqdm", "plain", "none"],
) -> None:
    # tqdm
    tqdm_pbar = None
    if progress_type == "tqdm":
        tqdm_pbar = tqdm()

    try:
        for output in ffmpeg_slice(
            ss=ss,
            to=to,
            input_path=input_path,
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

            if isinstance(output, FfmpegSliceResult):
                if tqdm_pbar is not None:
                    tqdm_pbar.clear()

                print(f"Output | {output}")
    finally:
        if tqdm_pbar is not None:
            tqdm_pbar.close()


def handle_slice_cli(args: Namespace) -> None:
    ss: str = args.ss
    to: str = args.to
    input_path_string: str = args.input_path
    output_path_string: str = args.output_path
    progress_type: str = args.progress_type

    input_path = Path(input_path_string)
    output_path = Path(output_path_string)

    if not validate_progress_type(progress_type):
        raise ValueError(f"Invalid progress_type: {progress_type}")

    execute_slice_cli(
        ss=ss,
        to=to,
        input_path=input_path,
        output_path=output_path,
        progress_type=progress_type,
    )


def add_arguments_slice_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-ss",
        type=str,
        required=True,
        help="Start time",
    )
    parser.add_argument(
        "-to",
        type=str,
        required=True,
        help="End time",
    )
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
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

    parser.set_defaults(handler=handle_slice_cli)
