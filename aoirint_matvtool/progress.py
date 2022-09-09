import sys
from datetime import timedelta
from typing import Iterable, Literal, Tuple, TypeVar, Union, get_args
from pydantic import BaseModel
from tqdm import tqdm

from .util import parse_ffmpeg_time_unit_syntax


class FfmpegProgressData(BaseModel):
  internal_fps: float
  internal_time_unit_syntax: str
  internal_frame: int

  input_video_fps: float
  input_video_start_time_unit_syntax: str

  @property
  def internal_timedelta(self) -> timedelta:
    return parse_ffmpeg_time_unit_syntax(self.internal_time_unit_syntax).to_timedelta()

  @property
  def input_video_start_timedelta(self) -> timedelta:
    return parse_ffmpeg_time_unit_syntax(self.input_video_start_time_unit_syntax).to_timedelta()

  @property
  def input_video_start_frame(self) -> int:
    return int(self.input_video_start_timedelta.total_seconds() * self.input_video_fps)

  @property
  def current_frame_as_input_video_scale(self) -> int:
    internal_current_frame = int(self.internal_frame / self.internal_fps * self.input_video_fps)
    return self.input_video_start_frame + internal_current_frame

  @property
  def current_timedelta_as_input_video_scale(self) -> timedelta:
    return self.input_video_start_timedelta + self.internal_timedelta


class FfmpegProgressLine(BaseModel):
  progress: FfmpegProgressData


ProgressType = Literal['tqdm', 'plain', 'none']
ProgressTypeValues = get_args(ProgressType)

T = TypeVar('T')


def iter_progress(
  iterable: Iterable[Union[T, FfmpegProgressLine]],
  progress_type: ProgressType,
) -> Iterable[Tuple[T, tqdm]]:
  if progress_type == 'tqdm':
    pbar = tqdm()

  def format_timedelta(td: timedelta) -> str:
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = td.microseconds

    return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{microseconds:06d}'

  try:
    for output in iterable:
      if isinstance(output, FfmpegProgressLine):
        internal_time_string = format_timedelta(output.internal_timedelta)
        internal_frame = output.internal_frame

        input_time_string = format_timedelta(output.current_timedelta_as_input_video_scale)
        input_frame = output.current_frame_as_input_video_scale

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

        continue

      yield output, pbar
  finally:
    if progress_type == 'tqdm':
      pbar.close()
