from pathlib import Path
import re
import subprocess
from typing import List, Optional
from pydantic import BaseModel

from . import config

class FfmpegCropScaleResult(BaseModel):
  success: bool
  message: Optional[str]
  stderr: str

def ffmpeg_crop_scale(input_path: Path, crop: str, scale: str, output_path: Path) -> FfmpegCropScaleResult:
  # TODO: quality control
  command = [
    config.FFMPEG_PATH,
    '-hide_banner',
    '-n', # fail if already exists
    '-i',
    str(input_path),
    '-filter:v',
    f'crop={crop},scale={scale}',
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
