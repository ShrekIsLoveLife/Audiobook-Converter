#!/usr/bin/env bash


SOURCE="${BASH_SOURCE[0]}"
DIR_LN="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PWD="$(pwd)"

touch "${DIR_LN}/activation_bytes.cache"
ln -s "${DIR_LN}/activation_bytes.cache"
ln -s "${DIR_LN}/aaxconvert.py"
ln -s "${DIR_LN}/duration.sh"
ln -s "${DIR_LN}/fileinfo.py"
ln -s "${DIR_LN}/gopoststuff-abook"
ln -s "${DIR_LN}/np_upload.sh"
ln -s "${DIR_LN}/_upload.sh"
ln -s "${DIR_LN}/upload.sh"
ln -s "${DIR_LN}/z_convert_all.sh"
# ln -s "${DIR_LN}/tables" tables
mkdir tables
mkdir tmp
#sudo mount -o bind "${DIR_LN}/tables" /opt/storage/aax/tables
sudo mount -o bind "${DIR_LN}/tables" tables

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

