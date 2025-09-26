from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.crop_scaler import CropScaler
from aoirint_matvtool.video_utility.fps_parser import FpsParser
from aoirint_matvtool.video_utility.image_finder import ImageFinder


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
    ffmpeg_path: str,
    fps_parser: FpsParser,
) -> ImageFinder:
    return ImageFinder(
        fps_parser=fps_parser,
        ffmpeg_path=ffmpeg_path,
    )
