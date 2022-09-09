from pathlib import Path
import re
import subprocess
from typing import Optional
from pydantic import BaseModel

from . import config
from .util import exclude_none


class FfmpegCropScaleResult(BaseModel):
  success: bool
  message: Optional[str]
  stderr: str


def ffmpeg_crop_scale(
  input_path: Path,
  crop: Optional[str],
  scale: Optional[str],
  video_codec: Optional[str],
  output_path: Path,
) -> FfmpegCropScaleResult:
  # TODO: quality control
  crop_filter_string = f'crop={crop}' if crop is not None else None
  scale_filter_string = f'scale={scale}' if scale is not None else None

  video_filters = list(exclude_none([
    crop_filter_string,
    scale_filter_string,
  ]))
  video_filter_opts = [ '-filter:v', ','.join(video_filters) ] if len(video_filters) != 0 else []

  video_codec_opts =  [ '-c:v', video_codec ] if video_codec is not None else []

  command = [
    config.FFMPEG_PATH,
    '-hide_banner',
    '-n', # fail if already exists
    '-i',
    str(input_path),
    *video_filter_opts,
    *video_codec_opts,
    '-c:a',
    'copy',
    '-map',
    '0',
    '-map_metadata',
    '0',
    str(output_path),
  ]
  proc = subprocess.run(command, stderr=subprocess.PIPE)
  stderr = proc.stderr.decode('utf-8')
  lines = stderr.splitlines()

  ret = proc.returncode
  if ret != 0:
    # skip Input or indented block to head the error message
    line_index = 0
    while line_index < len(lines):
      line = lines[line_index]
      match = re.search(r'^(Input|  ).+$', line)
      if not match:
        break
      line_index += 1

    message = '\n'.join(lines[line_index:]) if line_index != len(lines) else None

    return FfmpegCropScaleResult(
      success=False,
      message=message,
      stderr=stderr,
    )

  return FfmpegCropScaleResult(
    success=True,
    message=None,
    stderr=stderr,
  )
