import sys
from argparse import ArgumentParser, Namespace
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal, TypeGuard

from tqdm import tqdm

from ..progress_handler.base import ProgressHandler
from ..progress_handler.plain import ProgressHandlerPlain
from ..progress_handler.tqdm import ProgressHandlerTqdm
from ..video_utility.image_finder import ImageFinder, ImageFinderProgress, ImageFinderResult

from ..fps import ffmpeg_fps
from ..util import (
    format_timedelta_as_time_unit_syntax_string,
    get_real_start_timedelta_by_ss,
    parse_ffmpeg_time_unit_syntax,
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
) -> None:
    image_finder = ImageFinder(
        ffmpeg_path=ffmpeg_path,
    )

    # FPS
    input_video_fps = ffmpeg_fps(input_path=input_video_path).fps
    assert input_video_fps is not None, "FPS info not found in the input video"

    internal_fps = fps if fps is not None else input_video_fps

    # Time
    start_timedelta = get_real_start_timedelta_by_ss(video_path=input_video_path, ss=ss)

    progress_handler: ProgressHandler | None = None
    if progress_type == "tqdm":
        progress_handler = ProgressHandlerTqdm()
    elif progress_type == "plain":
        progress_handler = ProgressHandlerPlain(
            start_timedelta=start_timedelta,
            input_fps=input_video_fps,
            internal_fps=internal_fps,
        ) 


    # tqdm
    tqdm_pbar = None
    if progress_type == "tqdm":
        tqdm_pbar = tqdm()

    prev_input_timedelta = timedelta(seconds=-output_interval)


    async def _handle_progress(progress: ImageFinderProgress) -> None:
        if progress_handler is not None:
            await progress_handler.handle_progress(
                frame=progress.frame,
                time=progress.time,
                internal_frame=progress.internal_frame,
                internal_time=progress.internal_time,
            )
        
    async def _handle_result(result: ImageFinderResult) -> None:
        pass

    # TODO:
    # await image_finder.find_image(
    #     input_video_ss=ss,
    #     input_video_to=to,
    #     input_video_path=input_video_path,
    #     input_video_crop=input_video_crop,
    #     reference_image_path=reference_image_path,
    #     reference_image_crop=reference_image_crop,
    #     fps=fps,
    #     blackframe_amount=blackframe_amount,
    #     blackframe_threshold=blackframe_threshold,
    #     progress_handler=_handle_progress,
    #     result_handler=_handle_result,
    # )

    # Execute
    # for output in ffmpeg_find_image_generator(
    #     input_video_ss=ss,
    #     input_video_to=to,
    #     input_video_path=input_video_path,
    #     input_video_crop=input_video_crop,
    #     reference_image_path=reference_image_path,
    #     reference_image_crop=reference_image_crop,
    #     fps=fps,
    #     blackframe_amount=blackframe_amount,
    #     blackframe_threshold=blackframe_threshold,
    # ):
    #     if isinstance(output, FfmpegProgressLine):

    #     if isinstance(output, FfmpegBlackframeOutputLine):
    #         internal_timedelta = timedelta(seconds=output.t)
    #         internal_time_string = format_timedelta_as_time_unit_syntax_string(
    #             internal_timedelta
    #         )

    #         # 開始時間(ss)分、検出時刻を補正
    #         input_timedelta = start_timedelta + internal_timedelta
    #         input_time_string = format_timedelta_as_time_unit_syntax_string(
    #             input_timedelta
    #         )

    #         if (
    #             timedelta(seconds=output_interval)
    #             <= input_timedelta - prev_input_timedelta
    #         ):
    #             # 開始時間(ss)・フレームレート(fps)分、フレームを補正
    #             internal_frame = output.frame
    #             rescaled_output_frame = (
    #                 internal_frame / internal_fps * input_video_fps
    #             )
    #             input_frame = int(start_frame + rescaled_output_frame)

    #             if tqdm_pbar is not None:
    #                 tqdm_pbar.clear()

    #             print(
    #                 f"Output | Time {input_time_string}, frame {input_frame} (Internal time {internal_time_string}, frame {internal_frame})"  # noqa: E501
    #             )

    #             prev_input_timedelta = input_timedelta



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
