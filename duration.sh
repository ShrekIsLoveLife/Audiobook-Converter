#!/bin/bash
# call me with mp3length.sh directory
# e.g. ./mp3length . 
# or ./mp3length my-mp3-collection
# for file in $1/*.mp3
# do
#     echo -ne $file "\t"
#     ffmpeg -i "$file" 2>&1 | egrep "Duration"| cut -d ' ' -f 4 | sed s/,//
# done

find -print0 -name "*.m4b" -o -name "*.mp4" -o -name "*.mp3" | xargs -0 mplayer -vo dummy -ao dummy -identify 2>/dev/null | perl -nle '/ID_LENGTH=([0-9\.]+)/ && ($t +=$1) && printf "%d seconds\n",$t' | tail -n 1
find -print0 -name "*.m4b" -o -name "*.mp4" -o -name "*.mp3" | xargs -0 mplayer -vo dummy -ao dummy -identify 2>/dev/null | perl -nle '/ID_LENGTH=([0-9\.]+)/ && ($t +=$1) && printf "%02d:%02d:%02d\n",$t/3600,$t/60%60,$t%60' | tail -n 1
du -hs