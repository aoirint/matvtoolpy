# matvtoolpy / MultiAudioTrackVideoToolPy

A command line tool to handle a multi audio track video file.

マルチオーディオトラック動画ファイルを取り扱うためのコマンドラインツール

## インストール

基本的にFFmpegのラッパーです。別途FFmpegのインストールが必要です。
FFmpeg 4.2（Ubuntu 20.04の標準バージョン）および4.4（Ubuntu 22.04の標準バージョン）をサポートしています。

- <https://ffmpeg.org/download.html>

`matvtool`本体は、以下からダウンロード・インストールできます。
Pythonパッケージとして導入する場合、Python 3.11をサポートしています。

- バイナリ（Windows, Linux, macOS）
  - GitHub Release: <https://github.com/aoirint/matvtoolpy/releases>
- Pythonパッケージ: `pip3 install aoirint_matvtool`
  - PyPI: <https://pypi.org/project/aoirint-matvtool/>
- Dockerイメージ
  - Docker Hub: <https://hub.docker.com/r/aoirint/matvtoolpy>
    - CPU: `docker run --rm -v "$PWD:/work" aoirint/matvtoolpy:ubuntu-latest --help`
    - NVIDIA GPU: `docker run --rm --gpus all -v "$PWD:/work" aoirint/matvtoolpy:nvidia-latest --help`

## 用途

OBS Studioの録画機能やGeForce Experienceの録画機能などで作成した、マルチオーディオトラック動画ファイルを、
マルチオーディオトラックの状態を保ったまま簡易に編集し、後に高度な動画編集ソフトで使う素材として使いやすい形に整えるためのツール。

## 用例

### slice: クリップの作成

再エンコードしないため、高速ですが時間精度が低いです。
長時間の録画をおおまかに分割する用途を想定しています。
フレーム単位でクリップしたい場合、後段の動画編集ソフトで改めて加工してください。

```shell
matvtool slice -ss 00:05:00 -to 00:10:00 -i input.mkv output.mkv
```

### crop_scale: 切り取り・拡大縮小

`-vcodec`/`--video_codec`オプションで出力映像コーデックを指定できます（未指定時は既定のエンコーダを使用）。

```shell
# 左上1600x900を切り取って、1920x1080に拡大
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=0:y=0 --scale 1920:1080 output.mkv

# 右下1600x900を切り取って、1920x1080に拡大
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=iw-ow:y=ih-oh --scale 1920:1080 output.mkv

# 左上1600x900を切り取って、1920x1080に拡大、libx264でエンコード
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=0:y=0 --scale 1920:1080 -vcodec libx264 output.mkv

# 左上1600x900を切り取って、1920x1080に拡大、nvenc_h264でエンコード
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=0:y=0 --scale 1920:1080 -vcodec nvenc_h264 output.mkv

# 左上1600x900を切り取って、1920x1080に拡大、nvenc_hevcでエンコード
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=0:y=0 --scale 1920:1080 -vcodec nvenc_hevc output.mkv
```

### find_image: 画像の出現時間・出現フレームを検索

動画のスナップショットやクロップ画像を使用して、出現時間・出現フレームを検索します。
特定シーンの頭出しやチャプターを作成する用途を想定しています。
確実・正確に検出できるとは限りません。
出力は、VSCodeのマルチカーソル機能や`seq`コマンドなどを使って手動処理することを想定しています（試合1～試合10までの連番文字列生成：`seq -f "試合%g" 1 10`）。

`slice`と同様のオプションで検索範囲の時間を指定できます。`--fps`オプションで比較処理におけるフレームの読み飛ばしができます（コーデックにおけるフレーム間予測の関係で、全フレームのデコードは発生すると思われるため、デコード処理時間が支配的な場合はあまり意味がないと思われます）。
出力は、内部処理における時間・フレームと、入力動画における時間・フレームが併記されます。

`-icrop`/`--input_video_crop`オプション、`-refcrop`/`--reference_image_crop`オプションで、入力動画や参照画像の一部を使用した検索ができます。値は`crop_scale`の`--crop`オプションと同様です。
特定のアイコンが含まれることがわかっているが、フレーム中の他の部分が大きく違うケースの検索に有用です。

`-it`/`--output_interval`オプションで、連続出現時の出力を抑制できます。手動処理を減らすためのオプションです。
例えば、`-it 10`を指定すると、前回出現してから10秒間のフレームで再び出現を検出しても、ログ出力しません（[YouTubeのチャプター機能](https://support.google.com/youtube/answer/9884579)では、最小チャプター間隔は10秒）。

`-p`, `--progress_type`オプションで、処理の進捗状況の出力方法を変更できます。
値は、`tqdm` 標準エラー出力・インタラクティブシェル用（デフォルト）、`plain` 標準エラー出力・逐次出力、`none` 出力なし、が利用できます。

処理に時間のかかる長い動画を入力するときは、`tee`コマンドなどで出力を永続化したり、`tmux`コマンドなどでバックグラウンド処理したりすると便利です。うまく出力が表示されないときは、一時的に環境変数`PYTHONUNBUFFERED=1`を設定すると改善するかもしれません。

```shell
# reference.pngに一致するフレームを検索
matvtool find_image -i input.mkv -ref reference.png

# 10 FPSでreference.pngに一致するフレームを検索（フレームの読み飛ばしによる高速化を意図）
matvtool find_image -i input.mkv -ref reference.png --fps 10

# 左上1600x900を使用してreference.pngに一致するフレームを検索
matvtool find_image -i input.mkv -icrop w=1600:h=900:x=0:y=0 -ref reference.png -refcrop w=1600:h=900:x=0:y=0

# 最小10秒間隔で同上、10 FPS、出力永続化
PYTHONUNBUFFERED=1 matvtool find_image -i input.mkv -icrop w=1600:h=900:x=0:y=0 -ref reference.png -refcrop w=1600:h=900:x=0:y=0 --fps 10 -it 10 | tee chapters.txt
```

### audio: オーディオトラック一覧の確認

```shell
matvtool audio -i input.mkv
```

### select_audio: オーディオトラックを選択して新規動画ファイルとして出力

```shell
matvtool select_audio -i input.mkv --audio_index 2 3 -- output.mkv
```


## 開発

Python 3.11を使って開発しています。

### 依存関係

依存関係の管理に[Poetry](https://python-poetry.org/docs/#installation)を使っています。

```shell
# Pythonパッケージを追加
poetry add pydantic
poetry add --group dev pytest

# requirements*.txtを更新
poetry export --without-hashes -o requirements.txt
poetry export --without-hashes --with dev -o requirements-dev.txt
```
