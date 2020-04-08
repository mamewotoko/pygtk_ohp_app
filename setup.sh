#! /bin/bash
set -e

if [ "$(uname)" = Darwin ]; then
    brew update
    brew install pygobject3 gtk+3 python3
    pip3 install pycairo
elif [ -f /etc/lsb-release ]; then
    # debian, ubuntu
    sudo apt-get update
    sudo apt-get install -y python3 python3-dev python3-pip libgtk-3-dev pycairo
else
    echo unsupported os
    exit 1
fi
