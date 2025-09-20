from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Literal, TypeGuard

from ..progress_handler.base import ProgressHandler
from ..progress_handler.plain import ProgressHandlerPlain
from ..progress_handler.tqdm import ProgressHandlerTqdm
from ..video_utility.crop_scaler import (
    CropScaler,
    CropScalerProgress,
)


def validate_progress_type(value: Any) -> TypeGuard[Literal["tqdm", "plain", "none"]]:
    return value in ("tqdm", "plain", "none")


async def execute_crop_scale_cli(
    input_path: Path,
    output_path: Path,
    crop: str | None,
    scale: str | None,
    video_codec: str | None,
    progress_type: Literal["tqdm", "plain", "none"],
    ffmpeg_path: str,
) -> None:
    crop_scaler = CropScaler(
        ffmpeg_path=ffmpeg_path,
    )

    progress_handler: ProgressHandler | None = None
    if progress_type == "tqdm":
        progress_handler = ProgressHandlerTqdm()
    elif progress_type == "plain":
        progress_handler = ProgressHandlerPlain()

    async def _handle_progress(progress: CropScalerProgress) -> None:
        if progress_handler is not None:
            await progress_handler.handle_progress(
                frame=progress.frame,
                time=progress.time,
            )

    await crop_scaler.crop_scale(
        input_path=input_path,
        crop=crop,
        scale=scale,
        video_codec=video_codec,
        output_path=output_path,
        progress_handler=_handle_progress,
    )


async def handle_crop_scale_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    output_path_string: str = args.output_path
    crop: str | None = args.crop
    scale: str | None = args.scale
    video_codec: str | None = args.video_codec
    progress_type: str = args.progress_type
    ffmpeg_path: str = args.ffmpeg_path

    input_path = Path(input_path_string)
    output_path = Path(output_path_string)

    if not validate_progress_type(progress_type):
        raise ValueError(f"Invalid progress type: {progress_type}")

    await execute_crop_scale_cli(
        input_path=input_path,
        output_path=output_path,
        crop=crop,
        scale=scale,
        video_codec=video_codec,
        progress_type=progress_type,
        ffmpeg_path=ffmpeg_path,
    )


async def add_arguments_crop_scale_cli(parser: ArgumentParser) -> None:
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
