#!/usr/bin/env bash
# this just uploads a folder without processing

# get script directory
SOURCE="${BASH_SOURCE[0]}"
DIR_LN="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
# echo ${DIR_LN}
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

post_name=`cat usenet_name.txt 2>/dev/null`
# echo ${post_name}

if [ -z "${post_name}"  ]
then
	read -p "enter search string: " post_name
	echo Is this correct: "\"${post_name}\""
	read -p "Continue? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
else
	echo Is this correct: "\"${post_name}\""
	read -p "Continue? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
fi


cd "${post_name}"

cd ../
nyuu -C ~/.nyuu.conf.json --comment="${post_name}" -g 'alt.binaries.mp3.abooks' -O -o "${post_name}.nzb" "${post_name}"
# ${DIR}/gopoststuff-abook -v -g 'alt.binaries.mp3.abooks' -nzb "${post_name}.nzb" -rarpw "${post_name}" -d "${post_name}"
echo 
echo wait \(15 or so min\) for it to show up on:
echo "https://nzbindex.com/search/?q=${post_name}"
echo "https://nzbindex.com/search/?q=${post_name}"
echo "https://www.binsearch.info/?max=250&adv_age=&server=2&q=${post_name}"
echo
