from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.audio_track_title_parser import (
    AudioTrackTitleParser,
)


@pytest.mark.asyncio
async def test_audio_track_title_parser(
    audio_track_title_parser: AudioTrackTitleParser,
    fixture_dir: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"

    assert await audio_track_title_parser.parse_titles(
        input_path=input_file,
    ) == [
        "Sine 262Hz",
        "Sine 294Hz",
        "Sine 330Hz",
    ]
