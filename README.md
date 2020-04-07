GTK3でOHPシートのようなアプリ
=========================

## デモ

![#家にいよう](https://youtu.be/iN-biqblD2g)

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
### このアプリを起動中に後ろにあるアプリを操作したいのですが
いったん再消化するなどどかして、マウス、キー操作をしてください。

### なぜGTK?
ふと、やってみたくなったので。

### Ubuntuは
setup.shをubuntu向けに書くとできるはず(gtk3のインストール)

## ライセンス

Apache-2.0

----
Takashi Masuyama < mamewotoko@gmail.com >  
https://mamewo.ddo.jp/
