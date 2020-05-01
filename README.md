GTK3でOHPシートのようなアプリ [![Build Status](https://travis-ci.org/mamewotoko/pygtk_ohp_app.svg?branch=master)](https://travis-ci.org/mamewotoko/pygtk_ohp_app)
=========================

## デモ

[![](http://img.youtube.com/vi/iN-biqblD2g/0.jpg)](http://www.youtube.com/watch?v=iN-biqblD2g "家にいよう")

Macの写真アプリの上にアプリを起動して文字を書いてみました。

![windows10](image/windows10.png)

![ubuntu18.04](image/ubuntu1804.png) ![ubuntu20.04](image/ubuntu2004.png)


## 前提
以下のいずれかを準備してください

* [Homebrew](https://brew.sh/index_ja) がインストールされたMac
* Ubuntu (Linux)
  * [Ubuntu 18.04](https://www.ubuntulinux.jp/News/ubuntu1804)
  * [Ubuntu 20.04](https://releases.ubuntu.com/20.04/)
* [MSYS2](https://www.msys2.org/) がインストールされたWindows 10

## 使い方
### 準備
1. ターミナルを開いて、以下のコマンドを実行し、gtk+3などをインストールします。

    ```
    sh setup.sh
    ```

### 起動

1. 起動

    ```
    ./gtk3_ohp.py
    ```

赤枠の入った透明なWindowが画面いっぱいにに出ます。この上にマウスドラッグで絵が描けます。

### 操作方法

#### キーバインド

操作|キー
---------------|----------
元に戻す(undo)|Ctrl-z または Command-z
元に戻した操作のやり直し(redo)|Ctrl-y または Command-y
コピーした画像、テキストの貼り付け|Ctrl-v または Command-v
全削除|Ctrl-d または Command-d
高さを縮める、広げる|Ctrl-f または Command-f

テキスト、線の色変更

操作|キー
---------------|----------
レッド|Shift-r
ネイビー|Shift-n
グリーン|Shift-g
ピンク|Shift-p
ブラック|Shift-b
ホワイト|Shift-w
イエロー|Shift-y
むらさき|Shift-m
オレンジ|Shift-o
アクア|Shift-a

1 - 6キーで線の太さを変更

#### 起動時のコマンドラインオプション

* `-r` `--red`: float 0-1 ペンの色の赤成分
* `-g` `--green`: float 0-1 ペンの色の緑成分
* `-b` `--blue`: float 0-1 ペンの色の青成分
* `-l` `--line-width` ペンの太さ

## Q&A
### 用途は?

資料を表示して、その上に手書きで線を引いたり字を描きたい場合にお使いください。

### このアプリを起動中に後ろにあるアプリを操作したいのですが

いったん最小化するなどどかして、マウス、キー操作をしてください。

### なぜGTK?

ふと、やってみたくなったので。導入が面倒なのが難点ですが。

### 日本語を貼り付けるとトウフ □ が出るんですが

`-f` オプションで日本語フォント名を設定してください。

## TODO

* 改行つきの文字列のペーストをサポート
  * 例

    ```
    +-------------+
    |             |
    +-------------+
    ```
* 実行時に出る警告をなくす

    ```
    ./gtk3_ohp.py:55: DeprecationWarning: Gdk.Screen.get_width is deprecated
    self.width = screen.get_width()
    ./gtk3_ohp.py:56: DeprecationWarning: Gdk.Screen.get_height is deprecated
    self.height = screen.get_height() - STATUS_BAR_HEIGHT
    ```

## ライセンス

```
   Copyright 2020 Takashi Masuyama

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

----
Takashi Masuyama < mamewotoko@gmail.com >  
https://mamewo.ddo.jp/
