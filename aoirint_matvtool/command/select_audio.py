from argparse import ArgumentParser, Namespace
from contextlib import AsyncExitStack
from pathlib import Path

from ..progress_handler.base import ProgressHandler
from ..progress_handler.plain import ProgressHandlerPlain
from ..progress_handler.tqdm import ProgressHandlerTqdm
from ..video_utility.audio_selector import AudioSelector, AudioSelectorProgress
from ..video_utility.fps_parser import FpsParser
from ..video_utility.key_frame_parser import KeyFrameParser


async def execute_select_audio_cli(
    input_path: Path,
    audio_indexes: list[int],
    output_path: Path,
    progress_type: str,
    ffmpeg_path: str,
    ffprobe_path: str,
) -> None:
    fps_parser = FpsParser(
        ffprobe_path=ffprobe_path,
    )

    key_frame_parser = KeyFrameParser(
        fps_parser=fps_parser,
        ffprobe_path=ffprobe_path,
    )

    audio_selector = AudioSelector(
        fps_parser=fps_parser,
        key_frame_parser=key_frame_parser,
        ffmpeg_path=ffmpeg_path,
    )

    async with AsyncExitStack() as stack:
        progress_handler: ProgressHandler | None = None
        if progress_type == "tqdm":
            progress_handler = await stack.enter_async_context(ProgressHandlerTqdm())
        elif progress_type == "plain":
            progress_handler = await stack.enter_async_context(ProgressHandlerPlain())

        async def _handle_progress(progress: AudioSelectorProgress) -> None:
            if progress_handler is not None:
                await progress_handler.handle_progress(
                    frame=progress.frame,
                    time=progress.time,
                    internal_frame=progress.internal_frame,
                    internal_time=progress.internal_time,
                )

        await audio_selector.select_audio(
            input_path=input_path,
            audio_indexes=audio_indexes,
            output_path=output_path,
            progress_handler=_handle_progress,
        )


async def handle_select_audio_cli(args: Namespace) -> None:
    input_path_string: str = args.input_path
    audio_indexes: list[int] = args.audio_index
    output_path_string: str = args.output_path
    progress_type: str = args.progress_type
    ffmpeg_path: str = args.ffmpeg_path
    ffprobe_path: str = args.ffprobe_path

    input_path = Path(input_path_string)
    output_path = Path(output_path_string)

    await execute_select_audio_cli(
        input_path=input_path,
        audio_indexes=audio_indexes,
        output_path=output_path,
        progress_type=progress_type,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )


async def add_arguments_select_audio_cli(parser: ArgumentParser) -> None:
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
