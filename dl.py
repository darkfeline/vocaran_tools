#!/usr/bin/env python3

import os
import re
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import subprocess
import hashlib
import getopt
import sys

import stagger
from stagger.id3 import *

import parse

def dl(file, id, title, artist, album='', comment='', apic='def'):
    """Requests custom .mp3 from nicomimi.net

file should probably match name and end in '.mp3' as the right extension.
apic can be 'none' (no albumart), 'def' (default art), and an arbitrary number
of string depending on the song, thus: '1', '2', '3'  It's probably better to
either stick with 'def' or 'none'.

Replaced entirely by dl2(), as that function is superior to this one in
almost every single way.  This function will be kept for reference.

All dl functions should take the same arguments as this one and should have the
same return state, i.e. new file downloaded and tagged and everything else
unchanged.

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

def dl2(file, id, title, artist, album='', comment='', apic='def'):
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

# TODO doesn't work yet 
def dl3(file, id, title, artist, album='', comment='', apic='def'):
    """dl from nicosound, tagged with tag() (stagger)"""
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

# TODO not tested yet
def dl4(file, id, title, artist, album='', comment='', apic='def'):
    """Requests .mp3 download from nicomimi.net using wget and subprocess, then
tags file using stagger.

file should probably match name and end in '.mp3' as the right extension.
apic can be 'none' (no albumart), 'def' (default art), and an arbitrary number
of string depending on the song, thus: '1', '2', '3'  It's probably better to
either stick with 'def' or 'none'.

"""
    subprocess.call(['wget', 
                     'http://media2.nicomimi.net/get?vid={}'.format(id)])
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

def getsrc(outfile, number):
    """Downloads page source from Vocaloidism for Vocaran Week and saves in a
file."""
    conn = urllib.request.urlopen(
        'http://www.vocaloidism.com/weekly-vocaloid-ranking-{}/'.format(number))
    data = conn.read()
    with open(outfile, 'wb') as f:
        f.write(data)
    conn.close()

def load_session(sessionfile, filename):
    """Returns index from session file.  Uses filename to check md5sum.  """
    j = 0
    if os.path.isfile(sessionfile):
        print('Loading last session...')
        with open(sessionfile) as f:
            with open(filename) as g:
                if (hashlib.sha256(
                        g.read().encode('UTF-8')
                    ).hexdigest() != f.readline().rstrip()):
                    print("Dat file checksum differs from file;" +
                          "ignoring session")
                else:
                    j = int(f.readline())
    return j

def save_session(sessionfile, filename, i):
    """Save index to sessionfile)."""
    print('Writing current session...')
    with open(sessionfile, 'w') as f:
        with open(filename) as g:
            f.write(hashlib.sha256(
                g.read().encode('UTF-8')).hexdigest() + "\n")
            f.write(str(i + j))

def dlloop(dlf, fields, filename, optlist):
    """Loops a dl function over fields.  Prints output for convenience.  Also
handles pause/restore session.  file name illegal char handling is here ('/'
replaced with '|')
    
fields as returned from lsparse.  
dlf is the dl function to use.
filename is name of file (to generate session dat file).
optlist is list of arguments.

"""
    re_illegal = re.compile(r'/')
    re_error = re.compile(r'[Errno 110]')
    sessionfile= '.' + filename + '.dl.py.dat'
    # load session
    j = load_session(sessionfile, filename)
    fields = fields[j:]
    # loop over each dl
    for i, x in enumerate(fields):
        name = x[1] + '.mp3'
        name = re_illegal.sub('|', name)
        print("Fetching {} ({}/{})".format(
            name, i + j + 1, len(fields) + j))
        while True:
            try:
                dlf(name, *x)
            except KeyboardInterrupt as e:
                if 'i' in locals():
                    save_session(sessionfile, filename, i)
                sys.exit()
            except urllib.error.URLError as e:
                if re_error.search(str(e)):
                    if '-f' in [opt[0] for opt in optlist]:
                        print('URLError: retrying...')
                        continue
                    else:
                        save_session(sessionfile, i)
                        print('URLError: exiting...')
                        sys.exit()
            else:
                break
        print("Finished {} ({}/{})".format(
            name, i + j + 1, len(fields) + j))
    if os.path.isfile(sessionfile):
        os.remove(sessionfile)

def main(lst, optlist):
    """main function.  Parses file, adds empty fields, then passes on to
dlloop

lst is name of file
optlist is list of arguments

"""
    print('Parsing lst...')
    fields = parse.parse(lst)
    # set comment field to id if it doesn't exist
    for x in fields:
        if len(x) < 5:
            for i in range(4 - len(x)):
                x.append('')
            x.append(x[0])
    print('Downloading...')
    dlloop(dl2, fields, lst, optlist)
    print('Done.')

if __name__ == '__main__':
    import sys

    optlist, args = getopt.getopt(sys.argv[1:], 'f')
    lst = args[0]
    main(lst, optlist)
