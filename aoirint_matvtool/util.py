from datetime import timedelta
from math import log10
import re
from typing import Iterable, Optional, TypeVar
from pydantic import BaseModel


T = TypeVar('T')
def exclude_none(iterable: Iterable[Optional[T]]) -> Iterable[T]:
  """
    Type-safe exclusion function for None
  """
  for item in iterable:
    if item is None:
      continue

    yield item


class FfmpegTimeUnitSyntax(BaseModel):
  hours: int
  minutes: int
  seconds: int
  microseconds: int

  def to_timedelta(self) -> timedelta:
    return timedelta(hours=self.hours, minutes=self.minutes, seconds=self.seconds, microseconds=self.microseconds)


def integer_part_and_decimal_part_to_float(integer_part: int, decimal_part: int) -> float:
  ret = 0.0
  ret += integer_part

  decimal_part_num_digits = log10(decimal_part) if decimal_part != 0 else 0 # 桁数
  decimal_part_scale = 10 ** (-decimal_part_num_digits) # 桁補正係数

  ret += decimal_part * decimal_part_scale

  return ret


def parse_ffmpeg_time_unit_syntax(string: str) -> FfmpegTimeUnitSyntax:
  match = re.match(r'^(\d+):(\d+):(\d+)(\.\d+)?$', string) # HOURS:MM:SS.MILLISECONDS
  if match:
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    microseconds = int(match.group(4)[1:]) if match.group(4) is not None else 0 # maybe None

    return FfmpegTimeUnitSyntax(
      hours=hours,
      minutes=minutes,
      seconds=seconds,
      microseconds=microseconds,
    )

  match = re.match(r'^(\d+)(\.\d+)?$', string) # SECONDS
  if match:
    time_seconds_integer_part = int(match.group(1))
    time_seconds_decimal_part = int(match.group(2)) if match.group(2) is None else 0

    time_seconds = integer_part_and_decimal_part_to_float(integer_part=time_seconds_integer_part, decimal_part=time_seconds_decimal_part)

    td = timedelta(seconds=time_seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = td.microseconds

    return FfmpegTimeUnitSyntax(
      hours=hours,
      minutes=minutes,
      seconds=seconds,
      microseconds=microseconds,
    )

  raise ValueError(f'Unsupported syntax: {string}')
