import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Literal, TypeGuard

from tqdm import tqdm

from ..find_image import FfmpegProgressLine
from ..video_utility.crop_scaler import (
    CropScaler,
    FfmpegCropScaleResult,
)


def validate_progress_type(value: Any) -> TypeGuard[Literal["tqdm", "plain", "none"]]:
    return value in ("tqdm", "plain", "none")


def execute_crop_scale_cli(
    input_path: Path,
    output_path: Path,
    crop: str | None,
    scale: str | None,
    video_codec: str | None,
    progress_type: Literal["tqdm", "plain", "none"],
    ffmpeg_path: str,
    ffprobe_path: str,
) -> None:
    # tqdm
    tqdm_pbar = None
    if progress_type == "tqdm":
        tqdm_pbar = tqdm()

    crop_scaler = CropScaler(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )

    try:
        for output in crop_scaler.crop_scale(
            input_path=input_path,
            crop=crop,
            scale=scale,
            video_codec=video_codec,
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

            if isinstance(output, FfmpegCropScaleResult):
                if tqdm_pbar is not None:
                    tqdm_pbar.clear()

                print(f"Output | {output}")
    finally:
        if tqdm_pbar is not None:
            tqdm_pbar.close()


def handle_crop_scale_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    output_path_string: str = args.output_path
    crop: str | None = args.crop
    scale: str | None = args.scale
    video_codec: str | None = args.video_codec
    progress_type: str = args.progress_type
    ffmpeg_path: str = args.ffmpeg_path
    ffprobe_path: str = args.ffprobe_path

    input_path = Path(input_path_string)
    output_path = Path(output_path_string)

    if not validate_progress_type(progress_type):
        raise ValueError(f"Invalid progress type: {progress_type}")

    execute_crop_scale_cli(
        input_path=input_path,
        output_path=output_path,
        crop=crop,
        scale=scale,
        video_codec=video_codec,
        progress_type=progress_type,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )


def add_arguments_crop_scale_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        required=True,
        help="Input video file path",
    )
    parser.add_argument(
        "--crop",
        type=str,
        required=False,
        help="Crop parameter",
    )
    parser.add_argument(
        "--scale",
        type=str,
        required=False,
        help="Scale parameter",
    )
    parser.add_argument(
        "--video_codec",
        type=str,
        required=False,
        help="Output video codec",
    )
    parser.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=["tqdm", "plain", "none"],
        default="tqdm",
        help="Progress display type",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Output video file path",
    )

    parser.set_defaults(handler=handle_crop_scale_cli)
