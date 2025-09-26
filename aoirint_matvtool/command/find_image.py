from argparse import ArgumentParser, Namespace
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Literal, TypeGuard

from ..progress_handler.base import ProgressHandler
from ..progress_handler.plain import ProgressHandlerPlain
from ..progress_handler.tqdm import ProgressHandlerTqdm
from ..util import format_timedelta_as_time_unit_syntax_string
from ..video_utility.fps_parser import FpsParser
from ..video_utility.image_finder import (
    ImageFinder,
    ImageFinderProgress,
    ImageFinderResult,
)


def validate_progress_type(value: Any) -> TypeGuard[Literal["tqdm", "plain", "none"]]:
    return value in ("tqdm", "plain", "none")


async def execute_find_image_cli(
    ss: str | None,
    to: str | None,
    input_video_path: Path,
    input_video_crop: str | None,
    reference_image_path: Path,
    reference_image_crop: str | None,
    fps: int | None,
    blackframe_amount: int,
    blackframe_threshold: int,
    output_interval: float,
    progress_type: Literal["tqdm", "plain", "none"],
    ffmpeg_path: str,
    ffprobe_path: str,
) -> None:
    fps_parser = FpsParser(
        ffprobe_path=ffprobe_path,
    )

    image_finder = ImageFinder(
        fps_parser=fps_parser,
        ffmpeg_path=ffmpeg_path,
    )

    async with AsyncExitStack() as stack:
        progress_handler: ProgressHandler | None = None
        if progress_type == "tqdm":
            progress_handler = await stack.enter_async_context(ProgressHandlerTqdm())
        elif progress_type == "plain":
            progress_handler = await stack.enter_async_context(ProgressHandlerPlain())

    async def _handle_progress(progress: ImageFinderProgress) -> None:
        if progress_handler is not None:
            await progress_handler.handle_progress(
                frame=progress.frame,
                time=progress.time,
                internal_frame=progress.internal_frame,
                internal_time=progress.internal_time,
            )

    async def _handle_result(result: ImageFinderResult) -> None:
        internal_time_string = format_timedelta_as_time_unit_syntax_string(
            td=result.internal_time,
        )
        input_time_string = format_timedelta_as_time_unit_syntax_string(
            td=result.time,
        )

        if progress_handler is not None:
            await progress_handler.clear()

        print(
            (
                "Output | "
                f"Time {input_time_string}, "
                f"frame {result.frame} "
                f"(Internal time {internal_time_string}, "
                f"frame {result.internal_frame})"
            ),
        )

    await image_finder.find_image(
        input_video_ss=ss,
        input_video_to=to,
        input_video_path=input_video_path,
        input_video_crop=input_video_crop,
        reference_image_path=reference_image_path,
        reference_image_crop=reference_image_crop,
        fps=fps,
        blackframe_amount=blackframe_amount,
        blackframe_threshold=blackframe_threshold,
        output_interval=output_interval,
        progress_handler=_handle_progress,
        result_handler=_handle_result,
    )


async def handle_find_image_cli(args: Namespace) -> None:
    ss: str | None = args.ss
    to: str | None = args.to
    input_video_path_string: str = args.input_video_path
    input_video_crop: str | None = args.input_video_crop
    reference_image_path_string: str = args.reference_image_path
    reference_image_crop: str | None = args.reference_image_crop
    fps: int | None = args.fps
    blackframe_amount: int = args.blackframe_amount
    blackframe_threshold: int = args.blackframe_threshold
    output_interval: float = args.output_interval
    progress_type: str = args.progress_type
    ffmpeg_path: str = args.ffmpeg_path
    ffprobe_path: str = args.ffprobe_path

    input_video_path = Path(input_video_path_string)
    reference_image_path = Path(reference_image_path_string)

    if not validate_progress_type(progress_type):
        raise ValueError(f"Invalid progress type: {progress_type}")

    await execute_find_image_cli(
        ss=ss,
        to=to,
        input_video_path=input_video_path,
        input_video_crop=input_video_crop,
        reference_image_path=reference_image_path,
        reference_image_crop=reference_image_crop,
        fps=fps,
        blackframe_amount=blackframe_amount,
        blackframe_threshold=blackframe_threshold,
        output_interval=output_interval,
        progress_type=progress_type,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )


async def add_arguments_find_image_cli(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-ss",
        type=str,
        required=False,
        help="Start time",
    )
    parser.add_argument(
        "-to",
        type=str,
        required=False,
        help="End time",
    )
    parser.add_argument(
        "-i",
        "--input_video_path",
        type=str,
        required=True,
        help="Input video file path",
    )
    parser.add_argument(
        "-icrop",
        "--input_video_crop",
        type=str,
        required=False,
        help="Input video crop parameter",
    )
    parser.add_argument(
        "-ref",
        "--reference_image_path",
        type=str,
        required=True,
        help="Reference image file path",
    )
    parser.add_argument(
        "-refcrop",
        "--reference_image_crop",
        type=str,
        required=False,
        help="Reference image crop parameter",
    )
    parser.add_argument(
        "--fps",
        type=int,
        required=False,
        help="FPS",
    )
    parser.add_argument(
        "-ba",
        "--blackframe_amount",
        type=int,
        default=98,
        required=False,
        help="Blackframe amount",
    )
    parser.add_argument(
        "-bt",
        "--blackframe_threshold",
        type=int,
        default=32,
        required=False,
        help="Blackframe threshold",
    )
    parser.add_argument(
        "-it",
        "--output_interval",
        type=float,
        default=0,
        required=False,
        help="Minimum interval between outputs in seconds",
    )
    parser.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=("tqdm", "plain", "none"),
        default="tqdm",
        help="Progress display type",
    )

    parser.set_defaults(handler=handle_find_image_cli)
