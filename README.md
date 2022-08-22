# matvtoolpy / MultiAudioTrackVideoToolPy

A command line tool to handle a multi audio track video file.

マルチオーディオトラック動画ファイルを取り扱うためのコマンドラインツール

## インストール

基本的にFFmpegのラッパーです。別途FFmpegのインストールが必要です。

- <https://ffmpeg.org/download.html>

`matvtool`本体は、以下のリンクからダウンロード・インストールしてください。

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
matvtool crop_scale -i input.mkv -crop w=1600:h=900:x=0:y=0 -scale 1920:1080 output.mkv

# 右下1600x900を切り取って、1920x1080に拡大
matvtool crop_scale -i input.mkv -crop w=1600:h=900:x=iw-ow:y=ih-oh -scale 1920:1080 output.mkv
```

### audio: オーディオトラック一覧の確認

```shell
matvtool audio -i input.mkv
```

### select_audio: オーディオトラックを選択して新規動画ファイルとして出力

```shell
matvtool select_audio -i input.mkv --audio_index 2 3 -- output.mkv
```
