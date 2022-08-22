from pathlib import Path
import re
import subprocess
from typing import Optional
from pydantic import BaseModel

from . import config

class FfmpegSliceResult(BaseModel):
  success: bool
  message: Optional[str]
  stderr: str

def ffmpeg_slice(ss: str, to: str, input_path: Path, output_path: Path) -> FfmpegSliceResult:
  command = [
    config.FFMPEG_PATH,
    '-hide_banner',
    '-n', # fail if already exists
    '-ss',
    ss,
    '-to',
    to,
    '-i',
    str(input_path),
    '-map',
    '0',
    '-map_metadata',
    '0',
    '-c',
    'copy',
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

    return FfmpegSliceResult(
      success=False,
      message=message,
      stderr=stderr,
    )

  return FfmpegSliceResult(
    success=True,
    message=None,
    stderr=stderr,
  )
