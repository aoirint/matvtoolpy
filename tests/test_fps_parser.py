from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.fps_parser import FpsParser


@pytest.mark.asyncio
async def test_fps_parser(
    fps_parser: FpsParser,
    fixture_dir: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"

    assert await fps_parser.parse_fps(
        input_path=input_file,
    ) == pytest.approx(30.0, abs=0.1)
