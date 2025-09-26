from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.audio_track_title_parser import (
    AudioTrackTitleParser,
)
from aoirint_matvtool.video_utility.crop_scaler import CropScaler
from aoirint_matvtool.video_utility.fps_parser import FpsParser
from aoirint_matvtool.video_utility.image_finder import ImageFinder
from aoirint_matvtool.video_utility.key_frame_parser import KeyFrameParser
from aoirint_matvtool.video_utility.video_slicer import VideoSlicer


@pytest.fixture
def ffmpeg_path() -> str:
    return "ffmpeg"


@pytest.fixture
def ffprobe_path() -> str:
    return "ffprobe"


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def fps_parser(
    ffprobe_path: str,
) -> FpsParser:
    return FpsParser(
        ffprobe_path=ffprobe_path,
    )


@pytest.fixture
def crop_scaler(
    fps_parser: FpsParser,
    ffmpeg_path: str,
) -> CropScaler:
    return CropScaler(
        fps_parser=fps_parser,
        ffmpeg_path=ffmpeg_path,
    )


@pytest.fixture
def image_finder(
    fps_parser: FpsParser,
    ffmpeg_path: str,
    ffprobe_path: str,
) -> ImageFinder:
    return ImageFinder(
        fps_parser=fps_parser,
        key_frame_parser=KeyFrameParser(
            fps_parser=fps_parser,
            ffprobe_path=ffprobe_path,
        ),
        ffmpeg_path=ffmpeg_path,
    )


@pytest.fixture
def audio_track_title_parser(
    ffprobe_path: str,
) -> AudioTrackTitleParser:
    return AudioTrackTitleParser(
        ffprobe_path=ffprobe_path,
    )


@pytest.fixture
def key_frame_parser(
    fps_parser: FpsParser,
    ffprobe_path: str,
) -> KeyFrameParser:
    return KeyFrameParser(
        fps_parser=fps_parser,
        ffprobe_path=ffprobe_path,
    )


@pytest.fixture
def video_slicer(
    fps_parser: FpsParser,
    ffmpeg_path: str,
) -> VideoSlicer:
    return VideoSlicer(
        fps_parser=fps_parser,
        ffmpeg_path=ffmpeg_path,
    )
