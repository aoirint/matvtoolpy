from datetime import timedelta
from pathlib import Path

from ..video_utility.key_frame_parser import KeyFrameParser


class KeyFrameTimeFitter:
    def __init__(
        self,
        key_frame_parser: KeyFrameParser,
    ) -> None:
        self._key_frame_parser = key_frame_parser

    async def fit_time(
        self,
        video_path: Path,
        time: timedelta,
    ) -> timedelta:
        """
        FFmpeg の -ss オプションの挙動に合わせて、
        指定した時間に最も近く、指定した時間より前にあるキーフレームの時間を返す
        """

        key_frames = await self._key_frame_parser.parse_key_frames(
            input_path=video_path,
        )

        # キーフレーム情報をもとに time を補正
        output_time = timedelta(seconds=0)
        for key_frame in key_frames:
            # time より前のキーフレームを選択（-ss オプションの挙動）
            if time <= key_frame:
                break
            output_time = key_frame

        return output_time
