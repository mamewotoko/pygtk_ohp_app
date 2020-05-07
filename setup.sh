#! /bin/bash
set -ex

UNAME="$(uname)"

# TODO: venv?

if [ "$UNAME" = Darwin ]; then
    brew update
    which python
    python --version
    brew link --overwrite python
    brew install pygobject3
    brew install gtk+3 pkg-config
    python3 -m pip install -r requirements.txt

elif [ -f /etc/lsb-release ]; then
    # debian, ubuntu
    sudo apt-get update
    sudo apt-get install -y python3 python3-dev python3-pip libgtk-3-dev python3-setuptools xvfb pkg-config
    python3 -m pip install -r requirements.txt

elif [[ "$UNAME" == "MINGW64_NT"* ]] || [[ "$UNAME" == "MSYS_NT"* ]]; then
    # mingw64
    pacman -Syu --noconfirm
    pacman -Sy --noconfirm mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject 
    pacman -Sy --noconfirm mingw-w64-x86_64-python3-setuptools mingw-w64-x86_64-python3-pip
    python3 -m pip install -r requirements.txt

else
    echo unsupported os
    exit 1
fi
