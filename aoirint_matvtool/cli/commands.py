
from datetime import timedelta
from pathlib import Path
import sys
from tqdm import tqdm

from ..inputs import ffmpeg_get_input
from ..fps import ffmpeg_fps
from ..key_frames import FfmpegKeyFrameOutputLine, ffmpeg_key_frames
from ..slice import FfmpegSliceResult, ffmpeg_slice
from ..crop_scale import FfmpegCropScaleResult, ffmpeg_crop_scale
from ..find_image import FfmpegBlackframeOutputLine, FfmpegProgressLine, ffmpeg_find_image_generator
from ..select_audio import FfmpegSelectAudioResult, ffmpeg_select_audio
from ..util import (
  format_timedelta_as_time_unit_syntax_string,
  get_real_start_timedelta_by_ss,
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


def command_key_frames(args):
  input_path = Path(args.input_path)

  for output in ffmpeg_key_frames(
    input_path=input_path,
  ):
    if isinstance(output, FfmpegKeyFrameOutputLine):
      print(f'{output.time:.06f}')


def command_slice(args):
  ss = args.ss
  to = args.to
  input_path = Path(args.input_path)
  output_path = Path(args.output_path)
  progress_type = args.progress_type

  # tqdm
  pbar = None
  if progress_type == 'tqdm':
    pbar = tqdm()

  try:
    for output in ffmpeg_slice(
      ss=ss,
      to=to,
      input_path=input_path,
      output_path=output_path,
    ):
      if isinstance(output, FfmpegProgressLine):
        if progress_type == 'tqdm':
          pbar.set_postfix({
            'time': output.time,
            'frame': f'{output.frame}',
          })
          pbar.refresh()

        if progress_type == 'plain':
          print(f'Progress | Time {output.time}, frame {output.frame}', file=sys.stderr)

      if isinstance(output, FfmpegSliceResult):
        if progress_type == 'tqdm':
          pbar.clear()

        print(f'Output | {output}')
  finally:
    if progress_type == 'tqdm':
      pbar.close()


def command_crop_scale(args):
  input_path = Path(args.input_path)
  crop = args.crop
  scale = args.scale
  video_codec = args.video_codec
  output_path = Path(args.output_path)
  progress_type = args.progress_type

  # tqdm
  pbar = None
  if progress_type == 'tqdm':
    pbar = tqdm()

  try:
    for output in ffmpeg_crop_scale(
      input_path=input_path,
      crop=crop,
      scale=scale,
      video_codec=video_codec,
      output_path=output_path,
    ):
      if isinstance(output, FfmpegProgressLine):
        if progress_type == 'tqdm':
          pbar.set_postfix({
            'time': output.time,
            'frame': f'{output.frame}',
          })
          pbar.refresh()

        if progress_type == 'plain':
          print(f'Progress | Time {output.time}, frame {output.frame}', file=sys.stderr)

      if isinstance(output, FfmpegCropScaleResult):
        if progress_type == 'tqdm':
          pbar.clear()

        print(f'Output | {output}')
  finally:
    if progress_type == 'tqdm':
      pbar.close()


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
  output_interval = args.output_interval
  progress_type = args.progress_type

  # FPS
  input_video_fps = ffmpeg_fps(input_path=input_video_path).fps
  assert input_video_fps is not None, 'FPS info not found in the input video'

  internal_fps = fps if fps is not None else input_video_fps

  # Time
  start_timedelta = get_real_start_timedelta_by_ss(video_path=input_video_path, ss=ss)
  start_time_total_seconds = start_timedelta.total_seconds()
  start_frame = start_time_total_seconds * input_video_fps

  # tqdm
  pbar = None
  if progress_type == 'tqdm':
    pbar = tqdm()

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

        internal_time_string = format_timedelta_as_time_unit_syntax_string(internal_timedelta)

        # 開始時間(ss)分、検出時刻を補正
        input_timedelta = start_timedelta + internal_timedelta
        input_time_string = format_timedelta_as_time_unit_syntax_string(input_timedelta)

        # 開始時間(ss)・フレームレート(fps)分、フレームを補正
        internal_frame = output.frame
        rescaled_output_frame = internal_frame / internal_fps * input_video_fps
        input_frame = int(start_frame + rescaled_output_frame)

        if progress_type == 'tqdm':
          pbar.set_postfix({
            'time': input_time_string,
            'frame': f'{input_frame}',
            'internal_time': internal_time_string,
            'internal_frame': f'{internal_frame}',
          })
          pbar.refresh()

        if progress_type == 'plain':
          print(f'Progress | Time {input_time_string}, frame {input_frame} (Internal time {internal_time_string}, frame {internal_frame})', file=sys.stderr)

      if isinstance(output, FfmpegBlackframeOutputLine):
        internal_timedelta = timedelta(seconds=output.t)
        internal_time_string = format_timedelta_as_time_unit_syntax_string(internal_timedelta)

        # 開始時間(ss)分、検出時刻を補正
        input_timedelta = start_timedelta + internal_timedelta
        input_time_string = format_timedelta_as_time_unit_syntax_string(input_timedelta)

        if timedelta(seconds=output_interval) <= input_timedelta - prev_input_timedelta:
          # 開始時間(ss)・フレームレート(fps)分、フレームを補正
          internal_frame = output.frame
          rescaled_output_frame = internal_frame / internal_fps * input_video_fps
          input_frame = int(start_frame + rescaled_output_frame)

          if progress_type == 'tqdm':
            pbar.clear()

          print(f'Output | Time {input_time_string}, frame {input_frame} (Internal time {internal_time_string}, frame {internal_frame})')

          prev_input_timedelta = input_timedelta

  finally:
    if progress_type == 'tqdm':
      pbar.close()


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
  progress_type = args.progress_type

  # tqdm
  pbar = None
  if progress_type == 'tqdm':
    pbar = tqdm()

  try:
    for output in ffmpeg_select_audio(
      input_path=input_path,
      audio_indexes=audio_indexes,
      output_path=output_path,
    ):
      if isinstance(output, FfmpegProgressLine):
        if progress_type == 'tqdm':
          pbar.set_postfix({
            'time': output.time,
            'frame': f'{output.frame}',
          })
          pbar.refresh()

        if progress_type == 'plain':
          print(f'Progress | Time {output.time}, frame {output.frame}', file=sys.stderr)

      if isinstance(output, FfmpegSelectAudioResult):
        if progress_type == 'tqdm':
          pbar.clear()

        print(f'Output | {output}')
  finally:
    if progress_type == 'tqdm':
      pbar.close()
