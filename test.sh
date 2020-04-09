#! /bin/sh
set -x

if [ "$(uname)" = Darwin ]; then
    brew install coreutils
    date "+%Y%m%d-%H%H%S"
    gtimeout --preserve-status 10s ./gtk3_ohp.py
    date "+%Y%m%d-%H%H%S"
elif [ -f /etc/lsb-release ]; then
    sudo apt install
    date "+%Y%m%d-%H%H%S"
    xvfb-run timeout --preserve-status 10s ./gtk3_ohp.py
    date "+%Y%m%d-%H%H%S"
else
    echo unsupported platform
    exit 1
fi
