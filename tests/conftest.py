from pathlib import Path

import pytest


@pytest.fixture
def ffmpeg_path() -> str:
    return "ffmpeg"


@pytest.fixture
def ffprobe_path() -> str:
    return "ffprobe"


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"
