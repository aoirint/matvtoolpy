# matvtoolpy / MultiAudioTrackVideoToolPy

A command line tool to handle a multi audio track video file.

マルチオーディオトラック動画ファイルを取り扱うためのコマンドラインツール

## 用途

OBS Studioの録画機能やGeForce Experienceの録画機能などで作成した、マルチオーディオトラック動画ファイルを、
マルチオーディオトラックの状態を保ったまま簡易に編集し、後に高度な動画編集ソフトで使う素材として使いやすい形に整えるためのツール。

## 用例

### slice: クリップの作成

再エンコードしないため、高速ですが精度が低いです。
長時間の録画をおおまかに分割する用途を想定しています。
フレーム単位でクリップしたい場合、後段の動画編集ソフトで改めて加工してください。

```shell
matvtool slice -ss 00:05:00 -to 00:10:00 -i input.mkv output.mkv
```

### audio: オーディオトラック一覧の確認

```shell
matvtool audio -i input.mkv
```

### select_audio: オーディオトラックを選択して新規動画ファイルとして出力

```shell
matvtool select_audio -i input.mkv --audio_index 2 3 -- output.mkv
```
