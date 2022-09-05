
from datetime import timedelta
import logging
from math import floor
from pathlib import Path

from aoirint_matvtool import config
from aoirint_matvtool.inputs import ffmpeg_get_input
from aoirint_matvtool.fps import ffmpeg_fps
from aoirint_matvtool.slice import ffmpeg_slice
from aoirint_matvtool.crop_scale import ffmpeg_crop_scale
from aoirint_matvtool.select_audio import ffmpeg_select_audio
from aoirint_matvtool.find_image import ffmpeg_find_image_generator
from aoirint_matvtool.util import (
  parse_ffmpeg_time_unit_syntax,
)


def command_input(args):
  input_path = Path(args.input_path)
  print(ffmpeg_get_input(
    input_path=input_path,
  ))

def command_fps(args):
  input_path = Path(args.input_path)

  print(ffmpeg_fps(
    input_path=input_path,
  ).fps)

def command_slice(args):
  ss = args.ss
  to = args.to
  input_path = Path(args.input_path)
  output_path = Path(args.output_path)

  print(ffmpeg_slice(
    ss=ss,
    to=to,
    input_path=input_path,
    output_path=output_path,
  ))


def command_crop_scale(args):
  input_path = Path(args.input_path)
  crop = args.crop
  scale = args.scale
  output_path = Path(args.output_path)

  print(ffmpeg_crop_scale(
    input_path=input_path,
    crop=crop,
    scale=scale,
    output_path=output_path,
  ))


def command_audio(args):
  input_path = Path(args.input_path)

  inp = ffmpeg_get_input(
    input_path=input_path,
  )

  assert len(inp.streams) != 0
  stream = inp.streams[0]

  for track in stream.tracks:
    if track.type == 'Audio':
      metadata_title = next(filter(lambda metadata: metadata.key.lower() == 'title', track.metadatas), None)
      title = metadata_title.value if metadata_title else ''

      print(f'Audio Track {track.index}: {title}')


def command_select_audio(args):
  input_path = Path(args.input_path)
  audio_indexes = args.audio_index
  output_path = Path(args.output_path)

  print(ffmpeg_select_audio(
    input_path=input_path,
    audio_indexes=audio_indexes,
    output_path=output_path,
  ))


def command_find_image(args):
  ss = args.ss
  to = args.to
  input_video_path = Path(args.input_video_path)
  input_video_crop = args.input_video_crop
  reference_image_path = Path(args.reference_image_path)
  reference_image_crop = args.reference_image_crop
  fps = args.fps
  blackframe_amount = args.blackframe_amount
  blackframe_threshold = args.blackframe_threshold

  start_time = parse_ffmpeg_time_unit_syntax(ss) if ss is not None else None
  # end_time = parse_ffmpeg_time_unit_syntax(to) if to is not None else None

  input_video_fps = ffmpeg_fps(input_path=input_video_path).fps
  assert input_video_fps is not None, 'FPS info not found in the input video'

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
    raw_timedelta = timedelta(seconds=output.t)

    td = raw_timedelta
    raw_hours, remainder = divmod(td.seconds, 3600)
    raw_minutes, raw_seconds = divmod(remainder, 60)
    raw_microseconds = td.microseconds

    # 開始時間(ss)分、検出時刻を補正
    start_timedelta = timedelta(hours=start_time.hours, minutes=start_time.minutes, seconds=start_time.seconds, microseconds=start_time.microseconds) if start_time is not None else timedelta(seconds=0)

    td = start_timedelta + raw_timedelta
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = td.microseconds

    # 開始時間(ss)・フレームレート(fps)分、フレームを補正
    raw_frame = output.frame
    start_time_total_seconds = start_timedelta.total_seconds()

    output_fps = fps if fps is not None else input_video_fps

    start_frame = start_time_total_seconds * input_video_fps
    rescaled_output_frame = raw_frame / output_fps * input_video_fps

    frame = floor(start_frame + rescaled_output_frame)

    print(f'Time {hours:02d}:{minutes:02d}:{seconds:02d}.{microseconds:06d}, frame {frame} (Internal time {raw_hours:02d}:{raw_minutes:02d}:{raw_seconds:02d}.{raw_microseconds:06d}, frame {raw_frame})')


def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--log_level', type=int, default=logging.INFO)
  parser.add_argument('-f', '--ffmpeg_path', type=str, default=config.FFMPEG_PATH)

  subparsers = parser.add_subparsers()

  parser_input = subparsers.add_parser('input')
  parser_input.add_argument('-i', '--input_path', type=str, required=True)
  parser_input.set_defaults(handler=command_input)

  parser_fps = subparsers.add_parser('fps')
  parser_fps.add_argument('-i', '--input_path', type=str, required=True)
  parser_fps.set_defaults(handler=command_fps)

  parser_slice = subparsers.add_parser('slice')
  parser_slice.add_argument('-ss', type=str, required=True)
  parser_slice.add_argument('-to', type=str, required=True)
  parser_slice.add_argument('-i', '--input_path', type=str, required=True)
  parser_slice.add_argument('output_path', type=str)
  parser_slice.set_defaults(handler=command_slice)

  parser_crop_scale = subparsers.add_parser('crop_scale')
  parser_crop_scale.add_argument('-i', '--input_path', type=str, required=True)
  parser_crop_scale.add_argument('--crop', type=str, required=True)
  parser_crop_scale.add_argument('--scale', type=str, required=True)
  parser_crop_scale.add_argument('output_path', type=str)
  parser_crop_scale.set_defaults(handler=command_crop_scale)

  parser_audio = subparsers.add_parser('audio')
  parser_audio.add_argument('-i', '--input_path', type=str, required=True)
  parser_audio.set_defaults(handler=command_audio)

  parser_select_audio = subparsers.add_parser('select_audio')
  parser_select_audio.add_argument('-i', '--input_path', type=str, required=True)
  parser_select_audio.add_argument('--audio_index', type=int, nargs='+', required=True)
  parser_select_audio.add_argument('output_path', type=str)
  parser_select_audio.set_defaults(handler=command_select_audio)

  parser_find_image = subparsers.add_parser('find_image')
  parser_find_image.add_argument('-ss', type=str, required=False)
  parser_find_image.add_argument('-to', type=str, required=False)
  parser_find_image.add_argument('-i', '--input_video_path', type=str, required=True)
  parser_find_image.add_argument('-icrop', '--input_video_crop', type=str, required=False)
  parser_find_image.add_argument('-ref', '--reference_image_path', type=str, required=True)
  parser_find_image.add_argument('-refcrop', '--reference_image_crop', type=str, required=False)
  parser_find_image.add_argument('--fps', type=int, required=False)
  parser_find_image.add_argument('-ba', '--blackframe_amount', type=int, default=98)
  parser_find_image.add_argument('-bt', '--blackframe_threshold', type=int, default=32)
  parser_find_image.set_defaults(handler=command_find_image)

  args = parser.parse_args()

  log_level = args.log_level
  logging.basicConfig(
    level=log_level,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
  )

  config.FFMPEG_PATH = args.ffmpeg_path

  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()


if __name__ == '__main__':
  main()
