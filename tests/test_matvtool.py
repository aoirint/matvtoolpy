import sys
from pathlib import Path
from typing import Generator
sys.path.append(str(Path(__file__).parent.parent))

import contextlib
from unittest import TestCase
from tempfile import NamedTemporaryFile
import numpy as np
import cv2 # type: ignore
from aoirint_matvtool.fps import ffmpeg_fps


fourcc = cv2.VideoWriter_fourcc(*'mp4v')

@contextlib.contextmanager
def temporary_video_path() -> Generator[Path, None, None]:
  with NamedTemporaryFile(suffix='.mp4') as fp:
    width = 640
    height = 360
    fps = 60.0
    num_frames = 180

    font_face = cv2.FONT_HERSHEY_SIMPLEX

    video = cv2.VideoWriter(fp.name, fourcc, fps, (width, height))
    try:
      for frame_index in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        font_scale = cv2.getFontScaleFromHeight(
          fontFace=font_face,
          pixelHeight=32,
          thickness=1,
        )

        cv2.putText(
          img=frame,
          text=f'Frame {frame_index}/{num_frames}',
          org=(32, 32),
          fontFace=font_face,
          fontScale=font_scale,
          color=(255, 255, 255), # BGR
        )

        video.write(frame)
    finally:
      video.release()

    fp.flush()
    fp.seek(0)
    yield Path(fp.name)


class TestMatvTool(TestCase):
  def test_fps(self):
    with temporary_video_path() as video_path:
      fps = ffmpeg_fps(input_path=video_path).fps
      assert fps == 60.0
