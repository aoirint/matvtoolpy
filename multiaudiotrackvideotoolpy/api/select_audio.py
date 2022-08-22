from pathlib import Path
import re
import subprocess
from typing import List, Optional
from pydantic import BaseModel

from . import config

class FfmpegSelectAudioResult(BaseModel):
  success: bool
  message: Optional[str]
  stderr: str

def ffmpeg_select_audio(input_path: Path, audio_indexes: List[int], output_path: Path) -> FfmpegSelectAudioResult:
  audio_map_options = []
  for audio_index in audio_indexes:
    audio_map_options.append(f'-map')
    audio_map_options.append(f'0:a:{audio_index}')

  command = [
    config.FFMPEG_PATH,
    '-hide_banner',
    '-n', # fail if already exists
    '-i',
    str(input_path),
    '-map',
    '0:v:0',
    *audio_map_options,
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

    return FfmpegSelectAudioResult(
      success=False,
      message=message,
      stderr=stderr,
    )

  return FfmpegSelectAudioResult(
    success=True,
    message=None,
    stderr=stderr,
  )
