#! /bin/sh

if [ "$(uname)" = Darwin ]; then
    brew install coreutils
    gtimeout --preserve-status 10s ./gtk3_ohp.py
elif [ -f /etc/lsb-release ]; then
    sudo apt install
    xvfb-run timeout --preserve-status 10s ./gtk3_ohp.py
else
    echo unsupported platform
    exit 1
fi
