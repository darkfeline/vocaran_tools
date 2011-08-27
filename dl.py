#!/usr/bin/env python3

import os
import re
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar

import stagger
from stagger.id3 import *

import parse

def dl(file, id, title, artist, album='', comment='', apic='def'):
    """Requests custom .mp3 from nicomimi.net

file should probably match name and end in '.mp3' as the right extension.
apic can be 'none' (no albumart), 'def' (default art), and an arbitrary number
of string depending on the song, thus: '1', '2', '3'  It's probably better to
either stick with 'def' or 'none'.

Replaced entirely by altdl(), as that function is superior to this one in
almost every single way.  This function will be kept for reference.

"""
    params = urllib.parse.urlencode({'vid' : id,
                                     'access_key1' : 'hePj8S3ewMayA',
                                     'access_key2' : '13jsAnxfaKEE6',
                                     'APIC' : apic,
                                     'TIT2' : title,
                                     'TPE1' : artist,
                                     'TALB' : album,
                                     'USLT' : comment})
    params = params.encode('utf-8')

    #conn = None
    #for i in range(1, 6):
    #    try:
    #        conn = urllib.request.urlopen(
    #            'http://media{}.nicomimi.net/customplay.rb'.format(i), params)
    #        break
    #    except urllib.error.URLError:
    #        continue
    #    except Exception as err:
    #        print('-' * 60)
    #        print(err)
    #        print('Failed for ' + file)
    #        print('id: ' + id)
    #        print('title: ' + title)
    #        print('artist: ' + artist)
    #        print('album: ' + album)
    #        print('comment: ' + comment)
    #        print('apic: ' + apic)
    #        return
    #if not conn:
    #    raise Exception('100', 'all server timeout/unavailable')

    conn = urllib.request.urlopen(
        'http://media3.nicomimi.net/customplay.rb', params)

    data = conn.read()
    with open(file, 'wb') as f:
        f.write(data)
    conn.close()
    print('Finished ' + file)

def altdl(file, id, title, artist, album='', comment='', apic='def'):
    """Requests .mp3 download from nicomimi.net, then tags file using stagger.

file should probably match name and end in '.mp3' as the right extension.
apic can be 'none' (no albumart), 'def' (default art), and an arbitrary number
of string depending on the song, thus: '1', '2', '3'  It's probably better to
either stick with 'def' or 'none'.

"""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj))
    conn = opener.open('http://www.nicomimi.net/play/{}'.format(id))
    conn.close()

    conn = opener.open('http://media2.nicomimi.net/get?vid={}'.format(id)) 
    data = conn.read()
    with open(file, 'wb') as f:
        f.write(data)
    conn.close()

    tag(file, id, title, artist, album, comment, apic)

    print('Finished ' + file)

# unfinished
def dl2(file, id, title, artist, album='', comment='', apic='def'):
    """From nicosound"""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj))
    conn = opener.open("http://nicosound.anyap.info/sound/{}".format(id))
    html = conn.read()
    conn.close()

    params = urllib.parse.urlencode({'__EVENTTARGET' : eventtarget,
                                     '__EVENTARGUMENT' : eventargument,
                                     '__VIEWSTATE' : viewstate,
                                     '__EVENTVALIDATION' : eventvalidation
                                    })
    params = params.encode('utf-8')

    conn = opener.open("http://nicosound.anyap.info/sound/{}".format(id),
                       params)

    data = conn.read()
    with open(file, 'wb') as f:
        f.write(data)
    conn.close()

    tag(file, id, title, artist, album, comment, apic)

    print('Finished ' + file)

def tag(file, id, title, artist, album='', comment='', apic='def'):
    """Tags mp3 using stagger.  NOTE: comment is tagged as COMM, as opposed to
USLT that nicomimi.net custom uses for comments/lyrics."""
    # get pic
    getpic(file + '.jpg', id, apic)

    t = stagger.default_tag()
    t._filename = file
    t[TIT2] = title
    t[TPE1] = artist
    t[TALB] = album
    t[USLT] = USLT(text=comment)
    t[APIC] = APIC(file + '.jpg')
    t.write()

    # remove pic
    os.remove(file + '.jpg')

def getpic(file, id, apic='def'):
    """Gets art from nicomimi.net servers and saves to file"""
    param = ''
    try:
        if int(apic) > 0:
            param = '?aw=' + int(apic)
    except ValueError:
        pass

    conn = urllib.request.urlopen(
        'http://www.nicomimi.net/thumbnail/{}{}'.format(id, param))
    data = conn.read()
    with open(file, 'wb') as f:
        f.write(data)
    conn.close()

def dlloop(fields):
    """fields returned from lsparse."""
    a = re.compile(r'/')
    for x in fields:
        name = x[1] + '.mp3'
        name = a.sub('|', name)
        #dl(name, *x)
        altdl(name, *x)

def main(list):
    fields = parse.parse(list)
    # set comment field to id if it doesn't exist
    for x in fields:
        if len(x) < 5:
            for i in range(4 - len(x)):
                x.append('')
            x.append(x[0])
    dlloop(fields)

if __name__ == '__main__':
    import sys

    list = sys.argv[1]
    main(list)
