import asyncio
import logging
from argparse import ArgumentParser, Namespace
from asyncio import iscoroutinefunction

from . import __version__ as APP_VERSION
from . import config
from .command.audio import add_arguments_audio_cli
from .command.crop_scale import add_arguments_crop_scale_cli
from .command.find_image import add_arguments_find_image_cli
from .command.fps import add_arguments_fps_cli
from .command.key_frames import add_arguments_key_frames_cli
from .command.select_audio import add_arguments_select_audio_cli
from .command.slice import add_arguments_slice_cli


async def execute_main_cli(
    parser: ArgumentParser,
    args: Namespace,
    log_level: int,
    ffmpeg_path: str,
    ffprobe_path: str,
) -> None:
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
    )

    config.FFMPEG_PATH = ffmpeg_path
    config.FFPROBE_PATH = ffprobe_path

    if hasattr(args, "handler"):
        if iscoroutinefunction(args.handler):
            await args.handler(args)
        elif callable(args.handler):
            args.handler(args)
        else:
            parser.print_help()
    else:
        parser.print_help()


async def handle_main_cli(
    parser: ArgumentParser,
    args: Namespace,
) -> None:
    log_level: int = args.log_level
    ffmpeg_path: str = args.ffmpeg_path
    ffprobe_path: str = args.ffprobe_path

    await execute_main_cli(
        parser=parser,
        args=args,
        log_level=log_level,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )


async def add_arguments_main_cli(parser: ArgumentParser) -> None:
    parser.add_argument("-l", "--log_level", type=int, default=logging.INFO)
    parser.add_argument("-v", "--version", action="version", version=APP_VERSION)
    parser.add_argument("--ffmpeg_path", type=str, default=config.FFMPEG_PATH)
    parser.add_argument("--ffprobe_path", type=str, default=config.FFPROBE_PATH)

    subparsers = parser.add_subparsers()

    parser_fps = subparsers.add_parser("fps")
    await add_arguments_fps_cli(parser=parser_fps)

    parser_key_frames = subparsers.add_parser("key_frames")
    await add_arguments_key_frames_cli(parser=parser_key_frames)

    parser_slice = subparsers.add_parser("slice")
    await add_arguments_slice_cli(parser=parser_slice)

    parser_crop_scale = subparsers.add_parser("crop_scale")
    await add_arguments_crop_scale_cli(parser=parser_crop_scale)

    parser_find_image = subparsers.add_parser("find_image")
    await add_arguments_find_image_cli(parser=parser_find_image)

    parser_audio = subparsers.add_parser("audio")
    await add_arguments_audio_cli(parser=parser_audio)

    parser_select_audio = subparsers.add_parser("select_audio")
    await add_arguments_select_audio_cli(parser=parser_select_audio)


async def main_async() -> None:
    parser = ArgumentParser()
    await add_arguments_main_cli(parser=parser)

    args = parser.parse_args()
    await handle_main_cli(
        parser=parser,
        args=args,
    )


def main() -> None:
    asyncio.run(main_async())
