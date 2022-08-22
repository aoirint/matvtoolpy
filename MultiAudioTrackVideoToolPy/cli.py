
import logging
from pathlib import Path

from api import config
from api.inputs import ffmpeg_get_input
from api.slice import ffmpeg_slice


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
