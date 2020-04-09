#! /bin/bash
set -e

if [ "$(uname)" = Darwin ]; then
    brew update
    brew reinstall pygobject3 --with-python3
    brew install gtk+3 pkg-config
    python3 -m pip install wheel pycairo 
elif [ -f /etc/lsb-release ]; then
    # debian, ubuntu
    sudo apt-get update
    sudo apt-get install -y python3 python3-dev python3-pip libgtk-3-dev python3-setuptools xvfb pkg-config
    python3 -m pip install wheel pycairo
else
    echo unsupported os
    exit 1
fi
