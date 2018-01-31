#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Title:             AAX Audiobook Converter
# Version:           v1.0 (2017-11-13)
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
# from pprint import pprint
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
 █   ▒▒▒▒▒  ▓    ▓ ▓   ▓ ▓  ▓ ▓▓▓ .ws █
 █   ▒   ▒  ▓    ▓ ▓   ▓ ▓  ▓ ▓  ▓    █
 █  ▒    ▒  ▓    ▓ ▓▓▓▓  ▓▓▓▓ ▓   ▓   █
 █  ▒    ▒  ▓▓▓▓▓             ▓   ▓   █
 ██████████████████████████████████████'''

header_file_txt = ''' **************************************
 *     ##   %%%%%                     *
 *    #  #  %    %                    *
 *    #  #  %    %            %   %   *
 *    #  #  %    %            %   %   *
 *    #  #  %%%%%  %%%%% %%%  %  %    *
 *   #####  %    % %   % %  % %%% .ws *
 *   #   #  %    % %   % %  % %  %    *
 *  #    #  %    % %%%%  %%%% %   %   *
 *  #    #  %%%%%             %   %   *
 **************************************'''

nfo_post_template = '''

[hide][code]    DON'T POST THIS PART

Subject:
{meta:author_plain} - {meta:title_filtered} ({meta:date_orig}) {meta:series_formatted}

Password:
{meta:rar_passwd}

Search String:
abook.ws - {meta:instance_hash}

POST BELOW THIS LINE [/code][/hide]

[table]
[tr]
[td][img width=350]{meta:imgur_url}[/img][/td]
[td]      [/td]
[td][b]General Information[/b]
===================
[size=9pt]Title:   [color=white]{meta:title}[/color]
Author:   [color=white]{meta:author}[/color]
Read By:   [color=white]{meta:read_by}[/color]
Date:   [color=white]{meta:date}[/color]
Publisher:   [color=white]{meta:publisher}[/color]
Series:   [color=white]{meta:series}[/color]

[b]File Information[/b]
================
File Type:   [color=white]AAC/MP4[/color]
Source Format:   [color=white]Audible[/color]
Number of Chapters:   [color=white]{meta:chapters}[/color]
Total Duration:   [color=white]{meta:duration_clean}[/color]
Total Size:   [color=white]{meta:total_size}[/color]
Encoded At:   [color=white]Lossless Conversion[/color][/size]
[/td]
[/tr]
[/table]

[b]Book Description[/b]
================
{meta:comment}


[color=yellow]Posted by proxy[/color]
[color=yellow]Posted by proxy for[/color] [url=https://abook.ws/index.php?action=profile;u=][color=red]{meta:proxy_name}[/color][/url]


[hide]Search: [code]abook.ws - {meta:instance_hash}[/code][/hide]
[hide]Password: [code]{meta:rar_passwd}[/code][/hide]

[size=8pt][i]Note: These are not my rips. Many thanks to the original uploader(s).[/i][/size]
'''


nfo_template = '''

General Information
===================
'''
nfo_template += '{0: <25}'.format(' Title:') + '{meta:title}\n'
nfo_template += '{0: <25}'.format(' Author:') + '{meta:author}\n'
nfo_template += '{0: <25}'.format(' Read By:') + '{meta:read_by}\n'
# nfo_template += '{0: <25}'.format(' Copyright:') + '{meta:copyright}\n'
nfo_template += '{0: <25}'.format(' Date:') + '{meta:date}\n'
nfo_template += '{0: <25}'.format(' Publisher:') + '{meta:publisher}\n'
nfo_template += '{0: <25}'.format(' Series:') + '{meta:series}\n'
nfo_template += '''
File Information
================
'''
nfo_template += '{0: <25}'.format(' File Type:') + 'AAC/MP4\n'
nfo_template += '{0: <25}'.format(' Source Format:') + 'Audible\n'
nfo_template += '{0: <25}'.format(' Number of Chapters:') + '{meta:chapters}\n'
nfo_template += '{0: <25}'.format(' Total Duration:') + '{meta:duration_clean}\n'
nfo_template += '{0: <25}'.format(' Total Size:') + '{meta:total_size}\n'
nfo_template += '{0: <25}'.format(' Encoded At:') + 'Lossless Conversion\n'

nfo_template += '''
Book Description
================
{meta:comment}
'''

print ''
print header_file
print '      AAX Audiobook Converter v1.0\n         By "Shrek is Love"\nBTC: 1ANyHwihu9dL2CZ9LUZ48FdYTzyz8CCCFf\n'

prevlinect = 0
prevline = ''
def status_handler(line, chapter_info=None):
  global prevlinect, prevline
  if prevline == line and line != '':
    return
  prevline = line
  line = '          ' + line
  print (' ' * prevlinect) + '\r',
  if (chapter_info != None):
    matchObj = re.search( r'size=(.*?)time=(.*?)bitrate=(.*?)speed=(.*)$', line, re.M|re.I)
    if matchObj:
      currently_processed_time = matchObj.group(2).strip()
      speed = matchObj.group(4).strip()
      if '.' in currently_processed_time:
        currently_processed_time = currently_processed_time.split('.')[0]
      y = time.strptime(currently_processed_time,'%H:%M:%S')
      y_sec = datetime.timedelta(hours=y.tm_hour,minutes=y.tm_min,seconds=y.tm_sec).total_seconds()
      percent_done = int(round(y_sec / chapter_info['duration'] * 100, 0))
      m, s = divmod( timeit.default_timer() - chapter_info['process_start_time'], 60); h, m = divmod(m, 60)
      process_time =  "%02d:%02d:%02d" % (h, m, s)
      new_line = '     ' + str(percent_done) + '% - ' + currently_processed_time + ' / ' + chapter_info['duration_s'] + ' - ' + process_time + ' - Speed: ' + speed
      prevlinect = len(new_line)
      print new_line + '\r',
      return
    else:
      matchObj = re.search( r'size=(.*?)time=(.*?)bitrate=(.*?)$', line, re.M|re.I) # some versions don't have speed (ffmpeg 2.x)
      if matchObj:
        currently_processed_time = matchObj.group(2).strip()
        if '.' in currently_processed_time:
          currently_processed_time = currently_processed_time.split('.')[0]
        y = time.strptime(currently_processed_time,'%H:%M:%S')
        y_sec = datetime.timedelta(hours=y.tm_hour,minutes=y.tm_min,seconds=y.tm_sec).total_seconds()
        percent_done = int(round(y_sec / chapter_info['duration'] * 100, 0))
        m, s = divmod( timeit.default_timer() - chapter_info['process_start_time'], 60); h, m = divmod(m, 60)
        process_time =  "%02d:%02d:%02d" % (h, m, s)
        new_line = '     ' + str(percent_done) + '% - ' + currently_processed_time + ' / ' + chapter_info['duration_s'] + ' - ' + process_time
        prevlinect = len(new_line)
        print new_line + '\r',
        return
      else:
        prevlinect = len(line)
        print line + '\r',
        return
  else:
    prevlinect = len(line)
    print line + '\r',
    return



def pickle(fname, obj):
    # import cPickle, gzip
    cPickle.dump(obj=obj, file=gzip.open(fname, "wb", compresslevel=3), protocol=2)

def unpickle(fname):
    # import cPickle, gzip
    if os.path.isfile(fname):
      return cPickle.load(gzip.open(fname, "rb"))
    else:
      return {}


def run_cb_time(command, status_handler=None, chapter_info=None):
  # print ' '.join(command) # debug
  proc = subprocess.Popen(command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines = True)
  while True:
    line = proc.stdout.readline().strip()
    if line == '' and proc.poll() is not None:
        break
    if callable(status_handler):
      if 'time=' in line:
        status_handler(line, chapter_info=chapter_info)

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

def wrap(text, width=80):
    lines = []
    for paragraph in text.split('\n'):
        line = []
        len_line = 0
        for word in paragraph.split(' '):
            len_word = len(word)
            if len_line + len_word <= width:
                line.append(word)
                len_line += len_word + 1
            else:
                lines.append(' '.join(line))
                line = [word]
                len_line = len_word + 1
        lines.append(' '.join(line))
    return '\n'.join(lines)

def upload_imgur(image_file):
  # should add more debugging here
  try:
    f = open(image_file, "rb") # open our image file as read only in binary mode
    image_data = f.read()              # read in our image file
    b64_image = base64.standard_b64encode(image_data)
    client_id = "3e7a4deb7ac67da" # taken from https://github.com/Ceryn/img/blob/master/img.sh but you can get your own at https://api.imgur.com/oauth2/addclient select anon usage
    headers = {'Authorization': 'Client-ID ' + client_id}
    data = {'image': b64_image} # could include titles and other stuff https://api.imgur.com/endpoints/image
    request = urllib2.Request(url="https://api.imgur.com/3/upload.json", data=urllib.urlencode(data),headers=headers)
    response = urllib2.urlopen(request).read()
    parse = json.loads(response)
    return parse['data']['link']
  except:
    print '*** ERROR UPLOADING COVER ***'
    return 'ERROR_UPLOADING'

def replace_nfo_vars(nfo_file, fileinfo, is_template=False):
    nfo_file = re.sub(r'{meta:imgur_url}', fileinfo['meta']['imgur_url'], nfo_file)

    nfo_file = re.sub(r'{meta:title}', fileinfo['meta']['title'], nfo_file)
    nfo_file = re.sub(r'{meta:title_filtered}', fileinfo['meta']['title_filtered'], nfo_file)
    if 'author' in fileinfo['a_meta_data']:
      if is_template:
        item_info = ''
        item_cnt = 0
        for item_data in fileinfo['a_meta_data']['author']:
          if item_cnt > 0:
            item_info += ', '
          item_cnt+=1
          item_info += '[url=http://www.audible.com/search?advsearchKeywords=' + item_data + ']' + item_data + '[/url]'
        nfo_file = re.sub(r'{meta:author}', item_info, nfo_file)
        nfo_file = re.sub(r'{meta:author_plain}', ', '.join(fileinfo['a_meta_data']['author']), nfo_file)
      else:
        nfo_file = re.sub(r'{meta:author_plain}', ', '.join(fileinfo['a_meta_data']['author']), nfo_file)
        nfo_file = re.sub(r'{meta:author}', ', '.join(fileinfo['a_meta_data']['author']), nfo_file)
    else:
      if is_template:
        # should add split code here, but want to consolidate this more
        nfo_file = re.sub(r'{meta:author_plain}', ', '.join(fileinfo['meta']['artist']), nfo_file)
        nfo_file = re.sub(r'{meta:author}', '[url=http://www.audible.com/search?advsearchKeywords=' + fileinfo['meta']['artist'] + ']' + fileinfo['meta']['artist'] + '[/url]', nfo_file)
      else:
        nfo_file = re.sub(r'{meta:author_plain}', fileinfo['meta']['artist'], nfo_file)
        nfo_file = re.sub(r'{meta:author}', fileinfo['meta']['artist'], nfo_file)
    
    # nfo_file = re.sub(r'{meta:author}', fileinfo['meta']['artist'], nfo_file)

    if 'read_by' in fileinfo['a_meta_data']:
      if is_template:
        item_info = ''
        item_cnt = 0
        for item_data in fileinfo['a_meta_data']['read_by']:
          if item_cnt > 0:
            item_info += ', '
          item_cnt+=1
          item_info += '[url=http://www.audible.com/search?advsearchKeywords=' + item_data + ']' + item_data + '[/url]'
        nfo_file = re.sub(r'{meta:read_by}', item_info, nfo_file)
      else:
        nfo_file = re.sub(r'{meta:read_by}', ', '.join(fileinfo['a_meta_data']['read_by']), nfo_file)
    else:
      if is_template:
        # should add split code here, but want to consolidate this more
        nfo_file = re.sub(r'{meta:read_by}', '[url=http://www.audible.com/search?advsearchKeywords=' + fileinfo['meta']['read_by'] + ']' + fileinfo['meta']['artist'] + '[/url]', nfo_file)
      else:
        nfo_file = re.sub(r'{meta:read_by}', fileinfo['meta']['read_by'], nfo_file)
    
    # nfo_file = re.sub(r'{meta:read_by}', fileinfo['meta']['read_by'], nfo_file)
    nfo_file = re.sub(r'{meta:copyright}', fileinfo['meta']['copyright'], nfo_file)
    
    if 'date' in fileinfo['a_meta_data']:
      nfo_file = re.sub(r'{meta:date}', fileinfo['a_meta_data']['date'], nfo_file)
    else:
      nfo_file = re.sub(r'{meta:date}', fileinfo['meta']['date'], nfo_file)

    nfo_file = re.sub(r'{meta:date_orig}', fileinfo['meta']['date'], nfo_file)
      
    if 'publisher' in fileinfo['a_meta_data']:
      nfo_file = re.sub(r'{meta:publisher}', fileinfo['a_meta_data']['publisher'], nfo_file)
    else:
      nfo_file = re.sub(r'{meta:publisher}', fileinfo['meta']['publisher'], nfo_file)

    if 'rar_passwd' in fileinfo['a_meta_data']:
      nfo_file = re.sub(r'{meta:rar_passwd}', fileinfo['a_meta_data']['rar_passwd'], nfo_file)
    else:
      nfo_file = re.sub(r'{meta:rar_passwd}', 'unknown', nfo_file)

    if 'series' in fileinfo['a_meta_data']:
      nfo_file = re.sub(r'{meta:series}', fileinfo['a_meta_data']['series'], nfo_file)
      fileinfo['a_meta_data']['series_formatted'] = re.sub(r'N\/A', '', fileinfo['a_meta_data']['series'])
      nfo_file = re.sub(r'{meta:series_formatted}', fileinfo['a_meta_data']['series_formatted'], nfo_file)
    else:
      nfo_file = re.sub(r'{meta:series}', 'N/A', nfo_file)
      nfo_file = re.sub(r'{meta:series_formatted}', '', nfo_file)
    
    nfo_file = re.sub(r'{meta:album}', fileinfo['meta']['album'], nfo_file)
    nfo_file = re.sub(r'{meta:album_artist}', fileinfo['meta']['album_artist'], nfo_file)
    nfo_file = re.sub(r'{meta:series_position}', fileinfo['meta']['series_position'], nfo_file)
    nfo_file = re.sub(r'{meta:chapters}', str(fileinfo['meta']['num_chapters']), nfo_file)
    nfo_file = re.sub(r'{meta:duration_clean}', fileinfo['meta']['duration_clean'], nfo_file)
    nfo_file = re.sub(r'{meta:total_size}', fileinfo['meta']['total_size'], nfo_file)

    if 'description' in fileinfo['a_meta_data']:
      if is_template:
        nfo_file = re.sub(r'{meta:comment}', fileinfo['a_meta_data']['description'], nfo_file)
      else:
        nfo_file = re.sub(r'{meta:comment}', wrap(fileinfo['a_meta_data']['description'], 70), nfo_file)
    else:
      if is_template:
        nfo_file = re.sub(r'{meta:comment}', fileinfo['meta']['comment'], nfo_file)
      else:
        nfo_file = re.sub(r'{meta:comment}', wrap(fileinfo['meta']['comment'], 70), nfo_file)

    nfo_file = re.sub(r'{meta:proxy_name}', fileinfo['meta']['proxy_name'], nfo_file)
    nfo_file = re.sub(r'{meta:instance_hash}', fileinfo['meta']['instance_hash'], nfo_file)
    return nfo_file

def process_audiobook(filename, a_meta_data):
  print 'Extracting Audiobook Info...'

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
    if a_meta_data['type'] == 'aax':
      # checksum is provided in stderr
      matchObj = re.search( r'file checksum == (.*?)$', err, re.M|re.I)
      if matchObj:
        fileinfo['checksum'] = matchObj.group(1).strip()
      else:
        print 'Error: No checksum found for the aax file.'
        return

    data = json.loads(out)
    fileinfo['a_meta_data'] = a_meta_data
    fileinfo['chapters'] = data['chapters']
    fileinfo['meta'] = data['format']['tags']
    fileinfo['meta']['duration'] = float(data['format']['duration'])
    
    # fileinfo['meta']['file_title'] = fileinfo['meta']['artist'][:30] + ' (' + fileinfo['meta']['date'][:15] + ') ' + fileinfo['meta']['title'][:80]
    series_info = ''
    if 'series' in fileinfo['a_meta_data']:
      if fileinfo['a_meta_data']['series'].upper() != 'N/A':
        series_info = ' - ' + fileinfo['a_meta_data']['series'][:30]
    # fileinfo['meta']['file_title'] = fileinfo['meta']['artist'][:30] + series_info + ' - (' + fileinfo['meta']['date'][:15] + ') - ' + fileinfo['meta']['title'][:80]
    fileinfo['meta']['file_title'] = fileinfo['meta']['artist'][:30] + ' (' + fileinfo['meta']['date'][:15] + ') ' + fileinfo['meta']['title']

    fileinfo['meta']['file_title'] = re.sub('[^-a-zA-Z0-9_.() ]+', ' ', fileinfo['meta']['file_title'])
    fileinfo['meta']['title_filtered'] = re.sub(' \(Unabridged\)', '', fileinfo['meta']['title'])
    fileinfo['meta']['file_title_filtered'] = re.sub(' +', ' ', fileinfo['meta']['file_title'])
    fileinfo['meta']['file_title_filtered'] = re.sub(' \(Unabridged\)', '', fileinfo['meta']['file_title_filtered'] )[:150]

    m = hashlib.md5() # ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
    m.update("abook.ws")
    m.update(str(time.time()))
    m.update(fileinfo['meta']['file_title_filtered'])
    fileinfo['meta']['instance_hash'] =  re.sub('[^-a-zA-Z0-9_.() ]+', '', m.digest().encode("base64").strip()) #m.hexdigest()

    m, s = divmod(fileinfo['meta']['duration'], 60)
    h, m = divmod(m, 60)
    fileinfo['meta']['duration_clean'] = "%d:%02d:%02d" % (h, m, s)

    fileinfo['meta']['num_chapters'] = len(fileinfo['chapters'])

    print 'Creating directory: ' + fileinfo['meta']['file_title_filtered'] + '...'
    try:
      if not os.path.exists(fileinfo['meta']['file_title_filtered']):
        os.makedirs(fileinfo['meta']['file_title_filtered'])
      else:
        print 'Error: The folder "' + fileinfo['meta']['file_title_filtered'] + '"" Already Exists'
        return
    except OSError as e:
        if e.errno != errno.EEXIST:
          print 'Error: The folder "' + fileinfo['meta']['file_title_filtered'] + '"" Already Exists'
          return
          raise

    print 'Extracting Cover...'
    exitcode, out, err = run_get_exitcode_stdout_stderr([
      'ffmpeg', 
      '-y', 
      '-i', 
      filename, 
      os.path.join(fileinfo['meta']['file_title_filtered'],'cover.jpg')
      ], 
      '.' )

    if os.path.isfile(os.path.join(fileinfo['meta']['file_title_filtered'],'cover.jpg')):
      fileinfo['meta']['imgur_url'] = upload_imgur(os.path.join(fileinfo['meta']['file_title_filtered'],'cover.jpg'))
    else:
      fileinfo['meta']['imgur_url'] = 'ADD_IMAGE_URL'
    print 'Cover: ' + fileinfo['meta']['imgur_url']

    fileinfo['activation_bytes'] = ''
    if a_meta_data['type'] == 'aax':
      print 'Getting activation bytes for (' + fileinfo['checksum'] + ')...'
      activation_bytes_cache = unpickle(a_meta_data['activation_bytes_cache_file'])
      if (fileinfo['checksum'] in activation_bytes_cache):
        fileinfo['activation_bytes'] = activation_bytes_cache[fileinfo['checksum']]
        print '  (cache) -> ' + fileinfo['activation_bytes']
      else:
        tdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'tables')
        exitcode, out, err = run_get_exitcode_stdout_stderr([
            os.path.join(tdir, 'rcrack'), 
            '.', 
            '-h', 
            fileinfo['checksum'],
            ], 
            tdir )
        if exitcode == 0:
          matchObj = re.search( r'hex:(.*?)$', out, re.M|re.I)
          if matchObj:
            fileinfo['activation_bytes'] = matchObj.group(1).strip()
            print '    -> ' + fileinfo['activation_bytes']
            activation_bytes_cache[fileinfo['checksum']] = fileinfo['activation_bytes']
            pickle(a_meta_data['activation_bytes_cache_file'],activation_bytes_cache)
    else:
      fileinfo['activation_bytes'] = 'non-aax'

    if fileinfo['activation_bytes'] == '':
      print 'Error: No activation bytes discovered.'
    else:
      print 'Processing (' + str(fileinfo['meta']['num_chapters']) + ') chapters...'
      m3u = '#EXTM3U\n\n'
      zeropadct = str(len(str(fileinfo['meta']['num_chapters'])) + 1) # always have a 0 in front of largest number
      # chapter = fileinfo['chapters'][-1]
      # if True:
      processed = 0
      for chapter in fileinfo['chapters']:
        processed_percent = int(round(processed / (fileinfo['meta']['num_chapters'] + 0.0) * 100, 0))
        processed += 1
        padded_num = ('%0' + zeropadct + 'd') % ( chapter['id']+1 )
        chapter['filename'] = padded_num + ' ' + fileinfo['meta']['file_title_filtered'] + '.mp4'
        print '\n -> (' + str(processed_percent) + '%) ' + chapter['filename']
        if (chapter['id'] == 0):
          chapter['start_time'] = '2.0' # Remove 'This is Audible' from the beginning
        if (chapter['id'] == fileinfo['meta']['num_chapters'] -1):
          chapter['end_time'] = str( float(chapter['end_time']) - 4.0 ) # Remove 'Audible hopes you enjoyed this program' from the end
        chapter['duration'] = float(chapter['end_time']) - float(chapter['start_time'])
        m3u += '#EXTINF:' + str(chapter['duration']) + ',' + fileinfo['meta']['artist'] + ' - ' + fileinfo['meta']['title'] + '\n'
        m3u += chapter['filename'] + '\n\n'
        m, s = divmod( chapter['duration'], 60)
        h, m = divmod(m, 60)
        chapter['duration_s'] = "%02d:%02d:%02d" % (h, m, s)
        print '     Start: ' + chapter['start_time'] + '     End: ' + chapter['end_time'] + '       Duration: ' + chapter['duration_s']
        chapter_title_escaped = re.sub('"', '', (padded_num + ' - ' + chapter['tags']['title']) + ' - ' + fileinfo['meta']['title'])
        file_out = os.path.join(fileinfo['meta']['file_title_filtered'], chapter['filename'])
        # cmd = [
        #   'ffmpeg',
        #   '-y', 
        #   '-activation_bytes', fileinfo['activation_bytes'], 
        #   '-i', filename, 
        #   '-vn',
        #  '-c:a', 'aac',
        #   '-b:a', '80k',
        #   '-ac', '1',
        #    '-ss', chapter['start_time'],
        #   '-to', chapter['end_time'],
        #   '-metadata', 'title="' + chapter_title_escaped + '"', # I hate it when your player just says the book name and not chapter info
        #   '-metadata', 'track="' + str( chapter['id']+1 ) + '"',
        #   '-strict', '-2',  # needed for some versions of ffmpeg for aac
        #   file_out
        #   ]
        #
        if a_meta_data['type'] == 'aax':
          # lossless
          cmd = [
            'ffmpeg',
            '-y', 
            '-activation_bytes', fileinfo['activation_bytes'], 
            '-i', filename, 
            '-vn',
            '-c:a', 'copy',
             '-ss', chapter['start_time'],
            '-to', chapter['end_time'],
            '-metadata', 'title="' + chapter_title_escaped + '"', # I hate it when your player just says the book name and not chapter info
            '-metadata', 'track="' + str( chapter['id']+1 ) + '"',
            '-strict', '-2',  # needed for some versions of ffmpeg for aac
            file_out
            ]
        else:
          # lossless
          # Manual ffmpeg -y -i "name.m4b" -vn -c:a copy -metadata title="name" -metadata track="01" -strict -2 "name.mp4"
          cmd = [
            'ffmpeg',
            '-y', 
            '-i', filename, 
            '-vn',
            '-c:a', 'copy',
             '-ss', chapter['start_time'],
            '-to', chapter['end_time'],
            '-metadata', 'title="' + chapter_title_escaped + '"', # I hate it when your player just says the book name and not chapter info
            '-metadata', 'track="' + str( chapter['id']+1 ) + '"',
            '-strict', '-2',  # needed for some versions of ffmpeg for aac
            file_out
            ]

        chapter['process_start_time'] = timeit.default_timer()
        # exitcode, out, err = run_get_exitcode_stdout_stderr(cmd, '.'); print exitcode, out, err # debug version
        run_cb_time(cmd, status_handler=status_handler, chapter_info=chapter)
        status_handler(' ', chapter_info=None)
        if not os.path.isfile(file_out):
          print 'Error: Something went wrong, I could not fild the file we just created "' + chapter['filename'] + '"'
          return
        # break # debug single track
      print 'Creating m3u...'
      fh = open(os.path.join(fileinfo['meta']['file_title_filtered'],fileinfo['meta']['file_title_filtered'] + '.m3u'), 'w')
      fh.write(m3u) # Write out utf8 txt
      fh.close() 

      print 'Getting total size...'
      fileinfo['meta']['total_size'] = GetHumanReadable(getdirsize(fileinfo['meta']['file_title_filtered']))

      print 'Verifying NFO meta...'
      if ('imgur_url' not in fileinfo['meta'] ): fileinfo['meta']['imgur_url'] = 'IMGURL'
      if ('title' not in fileinfo['meta'] ): fileinfo['meta']['title'] = 'n/a'
      if ('title_filtered' not in fileinfo['meta'] ): fileinfo['meta']['title_filtered'] = 'n/a'
      if ('artist' not in fileinfo['meta'] ): fileinfo['meta']['artist'] = 'n/a'
      if ('read_by' not in fileinfo['meta'] ): fileinfo['meta']['read_by'] = 'n/a'
      if ('copyright' not in fileinfo['meta'] ): fileinfo['meta']['copyright'] = 'n/a'
      if ('date' not in fileinfo['meta'] ): fileinfo['meta']['date'] = 'n/a'
      if ('publisher' not in fileinfo['meta'] ): fileinfo['meta']['publisher'] = 'n/a'
      if ('series' not in fileinfo['meta'] ): fileinfo['meta']['series'] = 'n/a'
      if ('album' not in fileinfo['meta'] ): fileinfo['meta']['album'] = 'n/a'
      if ('album_artist' not in fileinfo['meta'] ): fileinfo['meta']['album_artist'] = 'n/a'
      if ('series_position' not in fileinfo['meta'] ): fileinfo['meta']['series_position'] = 'n/a'
      if ('num_chapters' not in fileinfo['meta'] ): fileinfo['meta']['num_chapters'] = 'n/a'
      if ('duration_clean' not in fileinfo['meta'] ): fileinfo['meta']['duration_clean'] = 'n/a'
      if ('total_size' not in fileinfo['meta'] ): fileinfo['meta']['total_size'] = 'n/a'
      if ('comment' not in fileinfo['meta'] ): fileinfo['meta']['comment'] = 'n/a'
      if ('proxy_name' not in fileinfo['meta'] ): fileinfo['meta']['proxy_name'] = 'n/a'
      if ('instance_hash' not in fileinfo['meta'] ): fileinfo['meta']['instance_hash'] = 'n/a'

      print 'Creating base NFO files...'
      nfo_file = replace_nfo_vars(nfo_template, fileinfo, False)
      nfo_file = re.sub(r'&#169;', '(c)', nfo_file)
      fh = open(os.path.join(fileinfo['meta']['file_title_filtered'],fileinfo['meta']['file_title_filtered'] + '.nfo'), 'w')
      # fh.write((header_file + nfo_file).encode("cp437", errors='replace')) # Write out proper NFO file
      fh.write((header_file + nfo_file).encode("cp437", errors='ignore')) # Write out proper NFO file
      fh.close() 
      # fh = open(os.path.join(fileinfo['meta']['file_title_filtered'],fileinfo['meta']['file_title_filtered'] + '.utf8.txt'), 'w')
      # fh.write(header_file + nfo_file) # Write out utf8 txt
      # fh.close() 
      # fh = open(os.path.join(fileinfo['meta']['file_title_filtered'],fileinfo['meta']['file_title_filtered'] + '.txt'), 'w')
      # fh.write(header_file_txt + nfo_file) # Write out utf8 txt
      # fh.close() 

      print 'Creating base Forum Template file...'
      nfo_file = replace_nfo_vars(nfo_post_template, fileinfo, True)
      nfo_file = re.sub(r'&#169;', '(c)', nfo_file)
      fh = open(os.path.join(fileinfo['meta']['file_title_filtered'],fileinfo['meta']['file_title_filtered'] + '.forum_template.txt'), 'w')
      fh.write(nfo_file) 
      fh.close() 

      fh = open(os.path.join(fileinfo['meta']['file_title_filtered'], 'usenet_name.txt'), 'w')
      fh.write('abook.ws - ' + fileinfo['meta']['instance_hash']) 
      fh.close() 

      fh = open(filename + '.processed', 'w')
      fh.write('processed')
      fh.close()
      print '\Folder:\n' + fileinfo['meta']['file_title_filtered']
      print '\nCover:\n' + fileinfo['meta']['imgur_url']
      print '\nSearch String:\nabook.ws - ' + fileinfo['meta']['instance_hash']
      print '\nDone :)\n'
      

if __name__ == "__main__":
  note = 'Note: If you can\'t see text you type after running this,\n       just type "reset" or "stty echo" and press enter.\n       (make sure you backspace if you typed)\n'

  cmd_line = 'Command Line is: ' + sys.argv[0] + ' path_to_filename.aax\n'



  if len(sys.argv) == 2:
    if len(sys.argv[1]) >= 4:
      if sys.argv[1][-4:].lower() == '.aax' or sys.argv[1][-4:].lower() == '.m4b' :
        if os.path.isfile(sys.argv[1]):
          print "Input = " + sys.argv[1]
          if not os.path.isfile(sys.argv[1] + '.processed'):
            a_meta_data = {}

            json_in = raw_input('Paste metadata: ').strip()
            if '--AMETA-BEGIN--' in json_in and '--AMETA-BEGIN--' in json_in:
              json_in = json_in.replace('--AMETA-BEGIN--','').replace('--AMETA-END--','')
              a_meta_data = json.loads(json_in)

            rar_passwd_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'rar.passwd')
            a_meta_data['rar_passwd'] = ''
            if os.path.isfile(rar_passwd_file):
              fh = open(rar_passwd_file, 'r') 
              a_meta_data['rar_passwd'] = fh.read() 
              fh.close() 
              if len(a_meta_data['rar_passwd']) == 0:
                print 'error: rar.passwd is empty'
                sys.exit(1)
            else:
              print 'error: rar.passwd is missing'
              sys.exit(1)    

            a_meta_data['activation_bytes_cache_file'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),'activation_bytes.cache')

            a_meta_data['type'] = sys.argv[1][-3:].lower()

            process_audiobook(sys.argv[1], a_meta_data)

          else:
            print note
            print cmd_line
            print 'Error: The aax file has a .processed file meaning it\'s already been worked on.'
        else:
          print note
          print cmd_line
          print 'Error: The path provided does not exist or I don\'t have permission to it.'
      else:
        print note
        print cmd_line
        print 'Error: I did not receive an aax file.'
    else:
      print note
      print cmd_line
      print 'Error: I did not receive an aax file.'
  else:
    print note
    print cmd_line
