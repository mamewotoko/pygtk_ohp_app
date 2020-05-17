#! /bin/bash
set -ex

UNAME="$(uname)"

# TODO: venv?

if [ "$UNAME" = Darwin ]; then
#    brew update
#    brew install pygobject3
    brew install gtk+3 pkg-config
    python3 -m pip install --user -r requirements.txt
    python3 -m pip install --user pygobject

elif [ -f /etc/lsb-release ]; then
    # debian, ubuntu
    sudo apt-get update
    sudo apt-get install -y python3 python3-dev python3-pip libgtk-3-dev python3-setuptools xvfb pkg-config
    python3 -m pip install --user -r requirements.txt

elif [ -f /etc/redhat-release ] && grep "release 7" /etc/redhat-release; then
    # redhat, centos7
    sudo yum install -y gcc gobject-introspection-devel cairo-devel \
         pkg-config python3-devel gtk3 python3-pip pygobject3-devel cairo-gobject-devel
    python3 -m pip install --user  PyGObject pycairo
    python3 -m pip install --user -r requirements.txt
    # install x11
    # http://morrey22.hatenablog.com/entry/2013/04/14/212837
    # sudo yum -y groups install "GNOME Desktop" 

# elif [ -f /etc/redhat-release ] && grep "release 8" /etc/redhat-release; then
#     # redhat, centos8
#     sudo yum install -y gcc cairo-devel \
#          pkg-config python3-devel gtk3 python3-pip cairo-gobject-devel
#     sudo python3 -m pip install PyGObject pycairo
#     sudo python3 -m pip install -r requirements.txt
#     # install x11
#     # http://morrey22.hatenablog.com/entry/2013/04/14/212837
#     # sudo yum -y groups install "GNOME Desktop" 

elif [[ "$UNAME" == "MINGW64_NT"* ]]; then
    # msys2 on PC
    pacman -Syu --noconfirm
    pacman -Sy --noconfirm mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject 
    pacman -Sy --noconfirm mingw-w64-x86_64-python3-setuptools mingw-w64-x86_64-python3-pip
    python3 -m pip install -r requirements.txt

elif [[ "$UNAME" == "MSYS_NT"* ]]; then
    # travis
    $msys2 pacman -Syu --noconfirm
    $msys2 pacman -Sy --noconfirm mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject 
    $msys2 pacman -Sy --noconfirm mingw-w64-x86_64-python3-setuptools mingw-w64-x86_64-python3-pip
    python3 -m pip install -r requirements.txt

else
    echo unsupported os
    exit 1
fi
