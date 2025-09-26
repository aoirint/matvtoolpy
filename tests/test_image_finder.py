from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.image_finder import ImageFinder, ImageFinderResult


@pytest.mark.asyncio
async def test_image_finder(
    image_finder: ImageFinder,
    fixture_dir: Path,
    tmp_path: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"
    reference_file = fixture_dir / "sample2.jpg"

    first_result: ImageFinderResult | None = None

    async def result_handler(result: ImageFinderResult) -> None:
        nonlocal first_result
        if first_result is None:
            first_result = result

    await image_finder.find_image(
        input_video_ss=None,
        input_video_to=None,
        input_video_path=input_file,
        input_video_crop=None,
        reference_image_path=reference_file,
        reference_image_crop=None,
        fps=None,
        blackframe_amount=95,
        blackframe_threshold=32,
        output_interval=0.0,
        progress_handler=None,
        result_handler=result_handler,
    )

    assert first_result is not None
    assert first_result.frame == 445
    assert first_result.time.total_seconds() == pytest.approx(14.8, abs=0.1)
    assert first_result.internal_frame == 445
    assert first_result.internal_time.total_seconds() == pytest.approx(14.8, abs=0.1)
