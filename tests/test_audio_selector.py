from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.audio_selector import AudioSelector
from aoirint_matvtool.video_utility.audio_track_title_parser import (
    AudioTrackTitleParser,
)


@pytest.mark.asyncio
async def test_audio_selector(
    audio_selector: AudioSelector,
    audio_track_title_parser: AudioTrackTitleParser,
    fixture_dir: Path,
    tmp_path: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"
    output_file = tmp_path / "output.mkv"

    await audio_selector.select_audio(
        input_path=input_file,
        audio_indexes=[
            1,
            2,
        ],
        output_path=output_file,
    )

    assert output_file.exists()

    assert await audio_track_title_parser.parse_titles(input_path=output_file) == [
        "Sine 294Hz",
        "Sine 330Hz",
    ]
