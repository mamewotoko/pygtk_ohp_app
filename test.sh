#! /bin/sh
set -x

UNAME=$(uname)

if [ "$UNAME" = Darwin ]; then
    brew install coreutils
    date "+%Y%m%d-%H%H%S"
    gtimeout --preserve-status 10s ./gtk3_ohp.py
    date "+%Y%m%d-%H%H%S"

elif [ -f /etc/lsb-release ]; then
    date "+%Y%m%d-%H%H%S"
    xvfb-run timeout --preserve-status 10s ./gtk3_ohp.py
    date "+%Y%m%d-%H%H%S"

elif [[ "$UNAME" == "MINGW64_NT"* ]] || [[ "$UNAME" == "MSYS_NT"* ]]; then

    date "+%Y%m%d-%H%H%S"
    timeout --preserve-status 10s ./gtk3_ohp.py
    date "+%Y%m%d-%H%H%S"
else
    echo unsupported platform
    exit 1
fi
