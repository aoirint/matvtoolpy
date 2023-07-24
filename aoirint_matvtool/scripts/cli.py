import logging
import sys
from argparse import ArgumentParser, Namespace
from datetime import timedelta
from pathlib import Path

from aoirint_matvtool import __VERSION__ as PACKAGE_VERSION
from aoirint_matvtool import config
from aoirint_matvtool.crop_scale import FfmpegCropScaleResult, ffmpeg_crop_scale
from aoirint_matvtool.find_image import (
    FfmpegBlackframeOutputLine,
    FfmpegProgressLine,
    ffmpeg_find_image_generator,
)
from aoirint_matvtool.fps import ffmpeg_fps
from aoirint_matvtool.inputs import ffmpeg_get_input
from aoirint_matvtool.key_frames import FfmpegKeyFrameOutputLine, ffmpeg_key_frames
from aoirint_matvtool.select_audio import FfmpegSelectAudioResult, ffmpeg_select_audio
from aoirint_matvtool.slice import FfmpegSliceResult, ffmpeg_slice
from aoirint_matvtool.util import (
    format_timedelta_as_time_unit_syntax_string,
    get_real_start_timedelta_by_ss,
    parse_ffmpeg_time_unit_syntax,
)
from tqdm import tqdm


def command_input(args: Namespace) -> None:
    input_path = Path(args.input_path)
    print(
        ffmpeg_get_input(
            input_path=input_path,
        )
    )


def command_fps(args: Namespace) -> None:
    input_path = Path(args.input_path)

    print(
        ffmpeg_fps(
            input_path=input_path,
        ).fps
    )


def command_key_frames(args: Namespace) -> None:
    input_path = Path(args.input_path)

    for output in ffmpeg_key_frames(
        input_path=input_path,
    ):
        if isinstance(output, FfmpegKeyFrameOutputLine):
            print(f"{output.time:.06f}")


def command_slice(args: Namespace) -> None:
    ss = args.ss
    to = args.to
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    progress_type = args.progress_type

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


def command_crop_scale(args: Namespace) -> None:
    input_path = Path(args.input_path)
    crop = args.crop
    scale = args.scale
    video_codec = args.video_codec
    output_path = Path(args.output_path)
    progress_type = args.progress_type

    # tqdm
    tqdm_pbar = None
    if progress_type == "tqdm":
        tqdm_pbar = tqdm()

    try:
        for output in ffmpeg_crop_scale(
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


def command_find_image(args: Namespace) -> None:
    ss = args.ss
    to = args.to
    input_video_path = Path(args.input_video_path)
    input_video_crop = args.input_video_crop
    reference_image_path = Path(args.reference_image_path)
    reference_image_crop = args.reference_image_crop
    fps = args.fps
    blackframe_amount = args.blackframe_amount
    blackframe_threshold = args.blackframe_threshold
    output_interval = args.output_interval
    progress_type = args.progress_type

    # FPS
    input_video_fps = ffmpeg_fps(input_path=input_video_path).fps
    assert input_video_fps is not None, "FPS info not found in the input video"

    internal_fps = fps if fps is not None else input_video_fps

    # Time
    start_timedelta = get_real_start_timedelta_by_ss(video_path=input_video_path, ss=ss)
    start_time_total_seconds = start_timedelta.total_seconds()
    start_frame = start_time_total_seconds * input_video_fps

    # tqdm
    tqdm_pbar = None
    if progress_type == "tqdm":
        tqdm_pbar = tqdm()

    prev_input_timedelta = timedelta(seconds=-output_interval)

    # Execute
    try:
        for output in ffmpeg_find_image_generator(
            input_video_ss=ss,
            input_video_to=to,
            input_video_path=input_video_path,
            input_video_crop=input_video_crop,
            reference_image_path=reference_image_path,
            reference_image_crop=reference_image_crop,
            fps=fps,
            blackframe_amount=blackframe_amount,
            blackframe_threshold=blackframe_threshold,
        ):
            if isinstance(output, FfmpegProgressLine):
                internal_time = parse_ffmpeg_time_unit_syntax(output.time)
                internal_timedelta = internal_time.to_timedelta()

                internal_time_string = format_timedelta_as_time_unit_syntax_string(
                    internal_timedelta
                )

                # 開始時間(ss)分、検出時刻を補正
                input_timedelta = start_timedelta + internal_timedelta
                input_time_string = format_timedelta_as_time_unit_syntax_string(
                    input_timedelta
                )

                # 開始時間(ss)・フレームレート(fps)分、フレームを補正
                internal_frame = output.frame
                rescaled_output_frame = internal_frame / internal_fps * input_video_fps
                input_frame = int(start_frame + rescaled_output_frame)

                if tqdm_pbar is not None:
                    tqdm_pbar.set_postfix(
                        {
                            "time": input_time_string,
                            "frame": f"{input_frame}",
                            "internal_time": internal_time_string,
                            "internal_frame": f"{internal_frame}",
                        }
                    )
                    tqdm_pbar.refresh()

                if progress_type == "plain":
                    print(
                        f"Progress | Time {input_time_string}, frame {input_frame} (Internal time {internal_time_string}, frame {internal_frame})",  # noqa: B950
                        file=sys.stderr,
                    )

            if isinstance(output, FfmpegBlackframeOutputLine):
                internal_timedelta = timedelta(seconds=output.t)
                internal_time_string = format_timedelta_as_time_unit_syntax_string(
                    internal_timedelta
                )

                # 開始時間(ss)分、検出時刻を補正
                input_timedelta = start_timedelta + internal_timedelta
                input_time_string = format_timedelta_as_time_unit_syntax_string(
                    input_timedelta
                )

                if (
                    timedelta(seconds=output_interval)
                    <= input_timedelta - prev_input_timedelta
                ):
                    # 開始時間(ss)・フレームレート(fps)分、フレームを補正
                    internal_frame = output.frame
                    rescaled_output_frame = (
                        internal_frame / internal_fps * input_video_fps
                    )
                    input_frame = int(start_frame + rescaled_output_frame)

                    if tqdm_pbar is not None:
                        tqdm_pbar.clear()

                    print(
                        f"Output | Time {input_time_string}, frame {input_frame} (Internal time {internal_time_string}, frame {internal_frame})"  # noqa: B950
                    )

                    prev_input_timedelta = input_timedelta

    finally:
        if tqdm_pbar is not None:
            tqdm_pbar.close()


def command_audio(args: Namespace) -> None:
    input_path = Path(args.input_path)

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


def command_select_audio(args: Namespace) -> None:
    input_path = Path(args.input_path)
    audio_indexes = args.audio_index
    output_path = Path(args.output_path)
    progress_type = args.progress_type

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


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-l", "--log_level", type=int, default=logging.INFO)
    parser.add_argument("-v", "--version", action="version", version=PACKAGE_VERSION)
    parser.add_argument("--ffmpeg_path", type=str, default=config.FFMPEG_PATH)
    parser.add_argument("--ffprobe_path", type=str, default=config.FFPROBE_PATH)

    subparsers = parser.add_subparsers()

    parser_input = subparsers.add_parser("input")
    parser_input.add_argument("-i", "--input_path", type=str, required=True)
    parser_input.set_defaults(handler=command_input)

    parser_fps = subparsers.add_parser("fps")
    parser_fps.add_argument("-i", "--input_path", type=str, required=True)
    parser_fps.set_defaults(handler=command_fps)

    parser_key_frames = subparsers.add_parser("key_frames")
    parser_key_frames.add_argument("-i", "--input_path", type=str, required=True)
    parser_key_frames.set_defaults(handler=command_key_frames)

    parser_slice = subparsers.add_parser("slice")
    parser_slice.add_argument("-ss", type=str, required=True)
    parser_slice.add_argument("-to", type=str, required=True)
    parser_slice.add_argument("-i", "--input_path", type=str, required=True)
    parser_slice.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=("tqdm", "plain", "none"),
        default="tqdm",
    )
    parser_slice.add_argument("output_path", type=str)
    parser_slice.set_defaults(handler=command_slice)

    parser_crop_scale = subparsers.add_parser("crop_scale")
    parser_crop_scale.add_argument("-i", "--input_path", type=str, required=True)
    parser_crop_scale.add_argument("--crop", type=str, required=False)
    parser_crop_scale.add_argument("--scale", type=str, required=False)
    parser_crop_scale.add_argument("-vcodec", "--video_codec", type=str, required=False)
    parser_crop_scale.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=("tqdm", "plain", "none"),
        default="tqdm",
    )
    parser_crop_scale.add_argument("output_path", type=str)
    parser_crop_scale.set_defaults(handler=command_crop_scale)

    parser_find_image = subparsers.add_parser("find_image")
    parser_find_image.add_argument("-ss", type=str, required=False)
    parser_find_image.add_argument("-to", type=str, required=False)
    parser_find_image.add_argument("-i", "--input_video_path", type=str, required=True)
    parser_find_image.add_argument(
        "-icrop", "--input_video_crop", type=str, required=False
    )
    parser_find_image.add_argument(
        "-ref", "--reference_image_path", type=str, required=True
    )
    parser_find_image.add_argument(
        "-refcrop", "--reference_image_crop", type=str, required=False
    )
    parser_find_image.add_argument("--fps", type=int, required=False)
    parser_find_image.add_argument("-ba", "--blackframe_amount", type=int, default=98)
    parser_find_image.add_argument(
        "-bt", "--blackframe_threshold", type=int, default=32
    )
    parser_find_image.add_argument("-it", "--output_interval", type=float, default=0)
    parser_find_image.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=("tqdm", "plain", "none"),
        default="tqdm",
    )
    parser_find_image.set_defaults(handler=command_find_image)

    parser_audio = subparsers.add_parser("audio")
    parser_audio.add_argument("-i", "--input_path", type=str, required=True)
    parser_audio.set_defaults(handler=command_audio)

    parser_select_audio = subparsers.add_parser("select_audio")
    parser_select_audio.add_argument("-i", "--input_path", type=str, required=True)
    parser_select_audio.add_argument(
        "--audio_index", type=int, nargs="+", required=True
    )
    parser_select_audio.add_argument(
        "-p",
        "--progress_type",
        type=str,
        choices=("tqdm", "plain", "none"),
        default="tqdm",
    )
    parser_select_audio.add_argument("output_path", type=str)
    parser_select_audio.set_defaults(handler=command_select_audio)

    args = parser.parse_args()

    log_level = args.log_level
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
    )

    config.FFMPEG_PATH = args.ffmpeg_path
    config.FFPROBE_PATH = args.ffprobe_path

    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
