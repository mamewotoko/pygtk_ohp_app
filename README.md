GTK3でOHPシートのようなアプリ [![Build Status](https://travis-ci.org/mamewotoko/pygtk_ohp_app.svg?branch=master)](https://travis-ci.org/mamewotoko/pygtk_ohp_app)
=========================

## デモ

[![](http://img.youtube.com/vi/iN-biqblD2g/0.jpg)](http://www.youtube.com/watch?v=iN-biqblD2g "家にいよう")

Macの写真アプリの上にアプリを起動して文字を書いてみました。

## 前提
* python3がインストールされたMac
* (UbuntuなどのLinuxは準備ができていないです)

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

## Q&A
### 用途は?
資料を表示して手書きで線を引いたり字を描きたい場合にお使いください。

### このアプリを起動中に後ろにあるアプリを操作したいのですが
いったん最小化するなどどかして、マウス、キー操作をしてください。

### なぜGTK?
ふと、やってみたくなったので。導入が面倒なのが難点ですが。

### Ubuntuは
setup.shをubuntu向けに書くとできるはず(gtk3のインストール)

## ライセンス

Apache-2.0

----
Takashi Masuyama < mamewotoko@gmail.com >  
https://mamewo.ddo.jp/
