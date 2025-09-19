from pathlib import Path

import pytest

from aoirint_matvtool.video_utility.crop_scaler import CropScaler


@pytest.fixture
def crop_scaler(
    ffmpeg_path: str,
    ffprobe_path: str,
) -> CropScaler:
    return CropScaler(
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )


def test_crop_scaler(
    crop_scaler: CropScaler,
    fixture_dir: Path,
    tmp_path: Path,
) -> None:
    input_file = fixture_dir / "sample1.mkv"
    output_file = tmp_path / "output.mkv"

    crop_scaler.crop_scale(
        input_path=input_file,
        crop="w=106:h=60:x=106:y=60",  # 320x180 の中央部分をクロップ
        scale="160:90",  # 160x90 にリサイズ
        video_codec="libx264",
        output_path=tmp_path / output_file,
    )

    assert output_file.exists()
    # TODO: 映像の比較
