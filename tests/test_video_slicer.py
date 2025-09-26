from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.video_slicer import VideoSlicer


@pytest.mark.asyncio
async def test_video_slicer(
    video_slicer: VideoSlicer,
    fixture_dir: Path,
    tmp_path: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"
    output_file = tmp_path / "output.mkv"

    await video_slicer.slice_video(
        input_path=input_file,
        ss="00:00:01",
        to="00:00:03",
        output_path=output_file,
    )

    assert output_file.exists()
    # TODO: 映像の比較
