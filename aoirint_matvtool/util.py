from datetime import timedelta
import re
from pydantic import BaseModel

class FfmpegTimeUnitSyntax(BaseModel):
  hours: int
  minutes: int
  seconds: int
  microseconds: int


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

  match = re.match(r'^(\d+)$', string) # SECONDS
  if match:
    time_seconds = match.group(3)

    td = timedelta(time_seconds)
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
