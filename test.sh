#! /bin/sh

if [ "$(uname)" = Darwin ]; then
    ./gtk3_ohp.py
elif [ -f /etc/lsb-release ]; then
    xfvb-run ./gtk3_ohp.py
else
    echo unsupported platform
    exit 1
fi
