# matvtoolpy / MultiAudioTrackVideoToolPy

A command line tool to handle a multi audio track video file.

マルチオーディオトラック動画ファイルを取り扱うためのコマンドラインツール

## インストール

基本的にFFmpegのラッパーです。別途FFmpegのインストールが必要です。

- <https://ffmpeg.org/download.html>

`matvtool`本体は、以下からダウンロード・インストールできます。

- バイナリ（Windows, Linux, macOS）
  - GitHub Release: <https://github.com/aoirint/matvtoolpy/releases>
- Pythonパッケージ: `pip3 install aoirint_matvtool`
  - PyPI: <https://pypi.org/project/aoirint-matvtool/>


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

```shell
# 左上1600x900を切り取って、1920x1080に拡大
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=0:y=0 --scale 1920:1080 output.mkv

# 右下1600x900を切り取って、1920x1080に拡大
matvtool crop_scale -i input.mkv --crop w=1600:h=900:x=iw-ow:y=ih-oh --scale 1920:1080 output.mkv
```

### find_image: 画像の出現時間・出現フレームを検索

動画のスナップショットやクロップ画像を使用して、出現時間・出現フレームを検索します。
特定シーンの頭出しやチャプターを作成する用途を想定しています。
確実・正確に検出できるとは限りません。フレームは動画編集ソフトなどで確認した場合と比べて、数フレーム前後することがあります。

`slice`と同様のオプションで検索範囲の時間を指定できます。`--fps`オプションでフレームの読み飛ばしができます。
出力は、内部処理における時間・フレームと、入力動画における時間・フレームが併記されます。

`-icrop`/`--input_video_crop`オプション、`-refcrop`/`--reference_image_crop`オプションで、入力動画や参照画像の一部を使用した検索ができます。値は`crop_scale`の`--crop`オプションと同様です。
特定のアイコンが含まれることがわかっているが、フレーム中の他の部分が大きく違うケースの検索に有用です。

```shell
# reference.pngに一致するフレームを検索
matvtool find_image -i input.mkv -ref reference.png

# 10 FPSでreference.pngに一致するフレームを検索（フレームの読み飛ばしによる高速化を意図）
matvtool find_image -i input.mkv -ref reference.png --fps 10

# 左上1600x900を使用してreference.pngに一致するフレームを検索
matvtool find_image -i input.mkv -icrop w=1600:h=900:x=0:y=0 -ref reference.png -refcrop w=1600:h=900:x=0:y=0
```

### audio: オーディオトラック一覧の確認

```shell
matvtool audio -i input.mkv
```

### select_audio: オーディオトラックを選択して新規動画ファイルとして出力

```shell
matvtool select_audio -i input.mkv --audio_index 2 3 -- output.mkv
```
