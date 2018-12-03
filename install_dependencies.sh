#!/usr/bin/env bash


SOURCE="${BASH_SOURCE[0]}"
DIR_LN="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PWD="$(pwd)"

sudo apt update 
sudo apt install build-essential git software-properties-common python-software-properties python2.7
sudo apt-add-repository multiverse
sudo add-apt-repository ppa:jcfp/sab-addons
sudo add-apt-repository ppa:jonathonf/ffmpeg-3
sudo apt-get update
sudo apt install atomicparsley cksfv rar unrar p7zip-full ffmpeg par2-tbb mplayer

git clone https://github.com/inAudible-NG/tables.git "${DIR_LN}/tables"

if [ ! -f rar.passwd ]; then
  echo '{change_me at rar.passwd}' > rar.passwd
  echo 'I had to create a rar.passwd file, please edit rar.passwd before using to set a rar password, make sure it is only one line'
fi
if [ ! -f ~/.gopoststuff.conf ]; then
  wget -O ~/.gopoststuff.conf https://raw.githubusercontent.com/ShrekIsLoveLife/gopoststuff-abook/master/sample.gopoststuff.conf
  echo 'I had to create a ~/.gopoststuff.conf please edit it'
fi

#     * # I like to make a tmpfs/ram disk to do processing on to speed things up
#     * mkdir /opt/ramdisk1
#     * sudo mount -t tmpfs -o size=8192m tmpfs /opt/ramdisk1
#     * Then run install_links.sh in this folder

