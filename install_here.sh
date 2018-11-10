#!/usr/bin/env bash

# get script directory
SOURCE="${BASH_SOURCE[0]}"
DIR_LN="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PWD="$(pwd)"
# echo ${DIR_LN}

sudo apt update 
sudo apt install build-essential git software-properties-common python-software-properties python2.7
sudo apt-add-repository multiverse
sudo add-apt-repository ppa:jcfp/sab-addons
sudo add-apt-repository ppa:jonathonf/ffmpeg-3
sudo apt-get update
sudo apt install atomicparsley cksfv rar unrar p7zip-full ffmpeg par2-tbb

git clone https://github.com/inAudible-NG/tables.git "${DIR_LN}/tables"
ln -s "${DIR_LN}/aaxconvert.py"
ln -s "${DIR_LN}/duration.sh"
ln -s "${DIR_LN}/fileinfo.py"
ln -s "${DIR_LN}/gopoststuff-abook"
ln -s "${DIR_LN}/np_upload.sh"
ln -s "${DIR_LN}/upload.sh"
ln -s "${DIR_LN}/z_convert_all.sh"
# ln -s "${DIR_LN}/tables" tables
mkdir tables
sudo mount -o bind "${DIR_LN}/tables" /opt/storage/aax/tables

if [ ! -f rar.passwd ]; then
  echo '{change_me at rar.passwd}' > rar.passwd
  echo 'I had to create a rar.passwd file, please edit rar.passwd before using to set a rar password, make sure it is only one line'
fi
if [ ! -f ~/.gopoststuff.conf ]; then
  wget -O ~/.gopoststuff.conf https://raw.githubusercontent.com/ShrekIsLoveLife/gopoststuff-abook/master/sample.gopoststuff.conf
  echo 'I had to create a ~/.gopoststuff.conf please edit it'
fi

#     * # I like to make a tmpfs/ram disk to do processing on to speed things up
#     * mkdir /opt/storage/aax/tmpfs1
#     * sudo mount -t tmpfs -o size=8192m tmpfs /opt/storage/aax/tmpfs1

# I find rcrack does not seem to work on openvz ubuntu 16
# ./rcrack . -h e05f5a2d96dc623dd07dc620d2cca77d782f455d
# git clone https://github.com/inAudible-NG/tables.git
# ./rcrack /opt/storage/dev/Audiobook-Converter/tables/ -h e05f5a2d96dc623dd07dc620d2cca77d782f455d
# alias wgeti='wget --no-check-certificate '
# wgeti 'https://github.com/inAudible-NG/tables/archive/master.zip'