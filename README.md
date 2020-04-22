GTK3でOHPシートのようなアプリ [![Build Status](https://travis-ci.org/mamewotoko/pygtk_ohp_app.svg?branch=master)](https://travis-ci.org/mamewotoko/pygtk_ohp_app)
=========================

## デモ

[![](http://img.youtube.com/vi/iN-biqblD2g/0.jpg)](http://www.youtube.com/watch?v=iN-biqblD2g "家にいよう")

Macの写真アプリの上にアプリを起動して文字を書いてみました。

## 前提
以下のいずれかを準備してください

* [Homebrew](https://brew.sh/index_ja) がインストールされたMac
* [Ubuntu 18.04](https://www.ubuntulinux.jp/News/ubuntu1804)

## 使い方
### 準備
1. gtk+3などをインストールします。

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

#### 起動時のオプション

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

日本語フォントの設定をサボっています。すいません。設定すると出ると思われます。

## TOGO
* 日本語の文字列のペーストをサポート
* 改行つきの文字列のペーストをサポート
  * 例

    ```
    +-------------+
    |             |
    +-------------+
    ```

## ライセンス

Apache-2.0

----
Takashi Masuyama < mamewotoko@gmail.com >  
https://mamewo.ddo.jp/
