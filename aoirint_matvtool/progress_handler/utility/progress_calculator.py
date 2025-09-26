from dataclasses import dataclass
from datetime import timedelta


@dataclass
class ProgressCalculatorResult:
    time: timedelta
    frame: int
    internal_time: timedelta
    internal_frame: int


class ProgressCalculator:
    def __init__(
        self,
        start_timedelta: timedelta,
        input_fps: float,
        internal_fps: float,
    ) -> None:
        self._start_timedelta = start_timedelta
        self._input_fps = input_fps
        self._internal_fps = internal_fps

    def calculate_progress(
        self,
        frame: int,
        time: timedelta,
    ) -> ProgressCalculatorResult:
        start_timedelta = self._start_timedelta
        input_video_fps = self._input_fps
        internal_fps = self._internal_fps

        start_time_total_seconds = start_timedelta.total_seconds()
        start_frame = start_time_total_seconds * input_video_fps

        # 開始時間(ss)分、検出時刻を補正
        input_timedelta = start_timedelta + time

        # 開始時間(ss)・フレームレート(fps)分、フレームを補正
        rescaled_output_frame = frame / internal_fps * input_video_fps
        input_frame = int(start_frame + rescaled_output_frame)

        return ProgressCalculatorResult(
            time=input_timedelta,
            frame=input_frame,
            internal_time=time,
            internal_frame=frame,
        )
