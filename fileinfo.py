#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Title:             File Info
# Version:           v1.0 (2018-03-08)
# Arthor:            "Shrek is Love"  BTC: 1ANyHwihu9dL2CZ9LUZ48FdYTzyz8CCCFf
# Original Arthor:   "Shrek is Love"  BTC: 1ANyHwihu9dL2CZ9LUZ48FdYTzyz8CCCFf
# License:           GNU GPLv3

# Features:
#   * Linux CLI conversion tool
#   * NFO creation (cp437, utf-8 txt, ansi txt) using aax meta data
#   * BBCode Post Template txt using aax meta data
#   * Search string generation
#   * Realtime output of conversion progress
#   * Chapter split using aax data
#   * 0 padding filenames
#   * Removal of 'This is Audible' and 'Audible hopes you enjoyed this program' 
#   * M3U playlist creation
#   * Extracting cover.png
#   * Creates folder based off aax meta data
#   * Subscript to convert all aax in folder
#   * Won't convert one already processing or processed (lock files/folders)
#   * Gets activation bytes using rcrack (inAudible-NG Tables)
#   * Accepts meta data from Audible (co.uk/.com) via bookmarklet
#   * Uploads cover to imgur

# How to Use:
#     Create a file called rar.passwd containing a single line of your rar password.
#        This is used for the template generator and the upload/archive script
#
#     ./aaxconvert.py <path_to_aax>
#        Process an aax file
#
#     ./z_aaxconvert_all.sh
#        Process all aax files in the current folder
#
#   After conversion edit the txt and nfo files to add more data and format text (may want to disable clickable links in settings/misc)
#   Use sublime3, wrap plus addon to auto wrap description text 
#     or
#     Use Notepad++ (32bit version only) and TextFX plugin (not compatiable with 64bit) [TextFX Edit->Rewrap] to auto wrap description text.
#   Adjust the password, imgur_url, author (if multiple, in template) read by/narriator, date, publisher, series position (if a series), description, take note of category
#
#   To read top of forum_template run the following in the converted folder:
#     head -n15 *.forum_template*

# Notes:
#     * You can edit the templates and headers from the top of this file's source code
#     * It's recommended that you run this in a tmux session
#     * Make sure this script is chmod +x
#     * This tool will make a .processed file if it is done
#          If a processed or directory already exists, this script will not run
#          Delete both of these if you would like to be able to run again and they exist
#     * If you can't see text you type after running this, 
#        just type "reset" and press enter. 
#        (make sure you backspace if you typed)

# Dependencies:
#     * Python 2.7: (sudo apt-get install python2.7)
#     * FFMPEG (preferably 3 and higher, 2 comes default on ubuntu):
#        sudo add-apt-repository ppa:jonathonf/ffmpeg-3
#        sudo add-apt-repository ppa:jonathonf/tesseract # for ubuntu 14.x 
#        sudo apt update && sudo apt upgrade, eh maybe just install ffmpeg package
#     * inAudible-NG Tables: (git clone https://github.com/inAudible-NG/tables.git)
#        tables needs to be a folder in the path of decode.py and rcrack needs +x
#        I believe the rcrack included is 64bit, you may need 32bit if your system is not 64bit.

# To-Do concepts:
#     * cache activation bytes - not sure if needed, hopefully this is a one time thing for the conversion
#     * activation bytes cli argument - I'll probably add this soon, it seems like a decent feature
#     * continue where left off - Hopefully pause/resume is not needed, but may want to add support
#     * adjustable encode settings - eh, maybe they will just modify this source, eh, let them do lossless conversion
#     * config file - for reusing settings and reducing cli length
#     * overwrite cli arg - will continue if it is processed or has a folder already

# GNU GPLv3 License:
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, re, os, errno, math
from subprocess import Popen, PIPE
import subprocess
import json, hashlib, time, datetime, timeit
from pprint import pprint
import gzip, cPickle

import urllib2, urllib, base64

reload(sys)  
sys.setdefaultencoding('utf8')













header_file = ''' ██████████████████████████████████████
 █     ▒▒   ▓▓▓▓▓                     █
 █    ▒  ▒  ▓    ▓                    █
 █    ▒  ▒  ▓    ▓            ▓   ▓   █
 █    ▒  ▒  ▓    ▓            ▓   ▓   █
 █    ▒  ▒  ▓▓▓▓▓  ▓▓▓▓▓ ▓▓▓  ▓  ▓    █
 █   ▒▒▒▒▒  ▓    ▓ ▓   ▓ ▓  ▓ ▓▓▓ .to █
 █   ▒   ▒  ▓    ▓ ▓   ▓ ▓  ▓ ▓  ▓    █
 █  ▒    ▒  ▓    ▓ ▓▓▓▓  ▓▓▓▓ ▓   ▓   █
 █  ▒    ▒  ▓▓▓▓▓             ▓   ▓   █
 ██████████████████████████████████████'''

print ''
print header_file
print '      File Info v1.0\n         By "Shrek is Love"\nBTC: 1ANyHwihu9dL2CZ9LUZ48FdYTzyz8CCCFf\n'

def run_get_exitcode_stdout_stderr(arr_cmd, arg_cwd):
  proc = Popen(arr_cmd, stdout=PIPE, stderr=PIPE, cwd=arg_cwd )
  out, err = proc.communicate()
  exitcode = proc.returncode
  return exitcode, out, err

def getdirsize(dir):  
  size = 0L  
  for root, dirs, files in os.walk(dir):  
    size += sum([os.path.getsize(os.path.join(root, name)) for name in files])  
  return size

def GetHumanReadable(size,precision=0):
    suffixes=[' b',' kb',' mb',' gb',' tb', ' pb', ' eb', ' zb', ' yb']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 8:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

def process_file(filename):
  print 'Extracting File Info...'

  exitcode, out, err = run_get_exitcode_stdout_stderr([
      'ffprobe', 
      '-v', 'info', 
      '-print_format', 'json', 
      '-show_format', 
      '-show_streams', 
      '-show_chapters', 
      filename
      ], 
      '.' )

  fileinfo = {}
  if exitcode == 0:

    data = json.loads(out)
    pprint(data)
    fileinfo['encoded_str'] = ''
    for stream in data['streams']:
      if stream['codec_type'] == 'audio':
        fileinfo['codec_name'] = stream['codec_name']
        fileinfo['bit_rate'] = stream['bit_rate']
        fileinfo['bit_rate_str'] = "%.2f kbps" % (int(stream['bit_rate']) / 1000.0)
        fileinfo['sample_rate'] = stream['sample_rate']
        fileinfo['sample_rate_str'] = "%.2f kHz" % (int(stream['sample_rate']) / 1000.0)
        fileinfo['channel_layout'] = stream['channel_layout'].capitalize()
        fileinfo['encoded_str'] = fileinfo['codec_name'].upper() + ': ' +  fileinfo['bit_rate_str'] + ', ' + fileinfo['sample_rate_str'] + ', ' + fileinfo['channel_layout']
        print fileinfo['encoded_str']
        break

    fileinfo['chapters'] = data['chapters']
    fileinfo['meta'] = data['format']['tags']
    fileinfo['meta']['duration'] = float(data['format']['duration'])
    

    m, s = divmod(fileinfo['meta']['duration'], 60)
    h, m = divmod(m, 60)
    fileinfo['meta']['duration_clean'] = "%d:%02d:%02d" % (h, m, s)

    fileinfo['meta']['num_chapters'] = len(fileinfo['chapters'])


    pprint(fileinfo)
    print '\n\n' + fileinfo['encoded_str']
    print '\nDone :)\n'
      

if __name__ == "__main__":
  note = 'Note: If you can\'t see text you type after running this,\n       just type "reset" or "stty echo" and press enter.\n       (make sure you backspace if you typed)\n'

  cmd_line = 'Command Line is: ' + sys.argv[0] + ' path_to_filename.aax\n'



  if len(sys.argv) == 2:
    if len(sys.argv[1]) >= 4:
        if os.path.isfile(sys.argv[1]):
          print "Input = " + sys.argv[1]
          process_file(sys.argv[1])

        else:
          print note
          print cmd_line
          print 'Error: The path provided does not exist or I don\'t have permission to it.'

  else:
    print note
    print cmd_line
