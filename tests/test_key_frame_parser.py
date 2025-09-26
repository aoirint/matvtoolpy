from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.key_frame_parser import KeyFrameParser


@pytest.mark.asyncio
async def test_key_frame_parser(
    key_frame_parser: KeyFrameParser,
    fixture_dir: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"

    key_frames = await key_frame_parser.parse_key_frames(
        input_path=input_file,
    )
    assert len(key_frames) == 4

    key_frame_seconds = [kf.total_seconds() for kf in key_frames]

    assert key_frame_seconds == [
        pytest.approx(0.023, abs=0.001),
        pytest.approx(6.323, abs=0.001),
        pytest.approx(10.190, abs=0.001),
        pytest.approx(17.490, abs=0.001),
    ]
