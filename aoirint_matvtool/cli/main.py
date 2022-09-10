import logging

from .. import config
from .commands import (
  command_input,
  command_fps,
  command_key_frames,
  command_slice,
  command_crop_scale,
  command_find_image,
  command_audio,
  command_select_audio,
)


def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--log_level', type=int, default=logging.INFO)
  parser.add_argument('--ffmpeg_path', type=str, default=config.FFMPEG_PATH)
  parser.add_argument('--ffprobe_path', type=str, default=config.FFPROBE_PATH)

  subparsers = parser.add_subparsers()

  parser_input = subparsers.add_parser('input')
  parser_input.add_argument('-i', '--input_path', type=str, required=True)
  parser_input.set_defaults(handler=command_input)

  parser_fps = subparsers.add_parser('fps')
  parser_fps.add_argument('-i', '--input_path', type=str, required=True)
  parser_fps.set_defaults(handler=command_fps)

  parser_key_frames = subparsers.add_parser('key_frames')
  parser_key_frames.add_argument('-i', '--input_path', type=str, required=True)
  parser_key_frames.set_defaults(handler=command_key_frames)

  parser_slice = subparsers.add_parser('slice')
  parser_slice.add_argument('-ss', type=str, required=True)
  parser_slice.add_argument('-to', type=str, required=True)
  parser_slice.add_argument('-i', '--input_path', type=str, required=True)
  parser_slice.add_argument('-p', '--progress_type', type=str, choices=('tqdm', 'plain', 'none'), default='tqdm')
  parser_slice.add_argument('output_path', type=str)
  parser_slice.set_defaults(handler=command_slice)

  parser_crop_scale = subparsers.add_parser('crop_scale')
  parser_crop_scale.add_argument('-i', '--input_path', type=str, required=True)
  parser_crop_scale.add_argument('--crop', type=str, required=False)
  parser_crop_scale.add_argument('--scale', type=str, required=False)
  parser_crop_scale.add_argument('-vcodec', '--video_codec', type=str, required=False)
  parser_crop_scale.add_argument('-p', '--progress_type', type=str, choices=('tqdm', 'plain', 'none'), default='tqdm')
  parser_crop_scale.add_argument('output_path', type=str)
  parser_crop_scale.set_defaults(handler=command_crop_scale)

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
  parser_find_image.add_argument('-it', '--output_interval', type=float, default=0)
  parser_find_image.add_argument('-p', '--progress_type', type=str, choices=('tqdm', 'plain', 'none'), default='tqdm')
  parser_find_image.set_defaults(handler=command_find_image)

  parser_audio = subparsers.add_parser('audio')
  parser_audio.add_argument('-i', '--input_path', type=str, required=True)
  parser_audio.set_defaults(handler=command_audio)

  parser_select_audio = subparsers.add_parser('select_audio')
  parser_select_audio.add_argument('-i', '--input_path', type=str, required=True)
  parser_select_audio.add_argument('--audio_index', type=int, nargs='+', required=True)
  parser_select_audio.add_argument('-p', '--progress_type', type=str, choices=('tqdm', 'plain', 'none'), default='tqdm')
  parser_select_audio.add_argument('output_path', type=str)
  parser_select_audio.set_defaults(handler=command_select_audio)

  args = parser.parse_args()

  log_level = args.log_level
  logging.basicConfig(
    level=log_level,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
  )

  config.FFMPEG_PATH = args.ffmpeg_path
  config.FFPROBE_PATH = args.ffprobe_path

  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()
