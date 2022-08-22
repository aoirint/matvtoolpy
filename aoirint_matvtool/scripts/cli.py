
import logging
from pathlib import Path

from aoirint_matvtool import config
from aoirint_matvtool.inputs import ffmpeg_get_input
from aoirint_matvtool.slice import ffmpeg_slice
from aoirint_matvtool.crop_scale import ffmpeg_crop_scale
from aoirint_matvtool.select_audio import ffmpeg_select_audio


def command_input(args):
  input_path = Path(args.input_path)
  print(ffmpeg_get_input(
    input_path=input_path,
  ))


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


def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--log_level', type=int, default=logging.INFO)
  parser.add_argument('-f', '--ffmpeg_path', type=str, default=config.FFMPEG_PATH)

  subparsers = parser.add_subparsers()

  parser_input = subparsers.add_parser('input')
  parser_input.add_argument('-i', '--input_path', type=str, required=True)
  parser_input.set_defaults(handler=command_input)

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
