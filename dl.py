#!/usr/bin/env python3

import os
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import hashlib

import stagger
from stagger.id3 import *

def dl(file, id, title='', artist='', album='', comment='', apic='def'):
    """Request a custom MP3 from nicomimi.net

    file should probably match the title and end in '.mp3' as the right
    extension.  apic can be 'none' (no albumart), 'def' (default art), and an
    arbitrary number of string depending on the song, thus: '1', '2', '3'  It's
    probably better to either stick with 'def' or 'none'.

    Replaced entirely by dl2(), as that function is superior to this one in
    almost every single way.  This function will be kept for reference.

    All dl functions should take the same arguments as this one and should have
    the same return state, i.e. new file downloaded and tagged and everything
    else unchanged.

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

    conn = urllib.request.urlopen(
        'http://media3.nicomimi.net/customplay.rb', params)

    data = conn.read()
    with open(file, 'wb') as f:
        f.write(data)
    conn.close()

def dl2(file, id, title='', artist='', album='', comment='', apic='def'):
    """Request an MP3 download from nicomimi.net, then tags file using stagger.

    file should probably match title and end in '.mp3' as the right extension.
    apic can be 'none' (no albumart), 'def' (default art), and an arbitrary
    number of string depending on the song, thus: '1', '2', '3'  It's probably
    better to either stick with 'def' or 'none'.

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
def dl3(file, id, title='', artist='', album='', comment='', apic='def'):
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

def tag(file, id, title='', artist='', album='', comment='', apic='def'):
    """Tag the MP3 file using stagger.  
    
    comment is tagged as COMM, as opposed to USLT that nicomimi.net custom uses
    for comments/lyrics.  
    
    apic can be 'none' (no albumart), 'def' (default art), and an arbitrary
    number of string depending on the song, thus: '1', '2', '3'  It's probably
    better to either stick with 'def' or 'none'.
    
    """
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
    """Get albumart from nicomimi.net servers and saves to file"""
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

def get_vocaloidism(outfile, number):
    """Download ranking page source from Vocaloidism.
    
    Get HTML source for the ranking page and save in given file.
    
    """
    conn = urllib.request.urlopen(
        'http://www.vocaloidism.com/weekly-vocaloid-ranking-{}/'.format(number))
    data = conn.read()
    with open(outfile, 'wb') as f:
        f.write(data)
    conn.close()

def load_session(sessionfile, filename):
    """Return the index from session file after checking md5sum.
    
    If the md5sum doesn't match, return -1.
    
    """
    j = -1
    if os.path.isfile(sessionfile):
        with open(sessionfile) as f:
            with open(filename) as g:
                if (hashlib.sha256(g.read().encode('UTF-8')).hexdigest() ==
                  f.readline().rstrip()):
                    j = int(f.readline())
    return j

def save_session(sessionfile, filename, i):
    """Save index to sessionfile with md5sum of song list file."""
    with open(sessionfile, 'w') as f:
        with open(filename) as g:
            f.write(hashlib.sha256(
                g.read().encode('UTF-8')).hexdigest() + "\n")
            f.write(str(i))

def main(*args):
    import argparse

    parser = argparse.ArgumentParser(description='dl.py')
    parser.add_argument('-f', dest='force', action='store_true', default=False)
    parser.add_argument('file')
    args = parse.parse_args(args)

    try:
        dlmain(args.file, args.force)
    except QuitException:
        import sys
        sys.exit()

def dlmain(filename, *args):
    """Parse song list file and pass on to dlloop

    filename is name of song list file.
    args is passed directly to dlloop().

    dlmain() sets comment field to id if it's blank.

    """

    import parse

    print('Parsing file...')
    fields = parse.parse_list(filename)
    # set comment field to id if it's blank
    for x in fields:
        if x[5] == '':
            x[5] = x[0]
    args = []
    if '-f' in optlist:
        args.append(True)
    else:
        args.append(False)
    print('Downloading...')
    try:
        dlloop(dl2, fields, filename, *args)
    except QuitException as e:
        raise e
    print('Done.')

def dlloop(dlf, fields, filename, force=False):
    """Loop the dl function over fields.

    Prints output for convenience.  Also handle pause/restore session.  File
    name illegal char handling is here ('/' replaced with '|')

    fields is the song list.
    dlf is the dl function to use.
    filename is the name of the song list file (to generate session dat file).
    force is boolean for whether to retry downloads on timeout.

    """
    import re
    re_illegal = re.compile(r'/')
    re_error = re.compile(r'[Errno 110]')
    sessionfile= '.' + filename + '.dl.py.dat'
    # load session
    print('Loading last session...')
    j = load_session(sessionfile, filename)
    if j < 0:
        print("Data file checksum differs from file; ignoring session")
        j = 0
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
                    print('Writing current session...')
                    save_session(sessionfile, filename, i + j)
                raise QuitException()
            except urllib.error.URLError as e:
                if re_error.search(str(e)):
                    if force:
                        print('URLError: retrying...')
                        continue
                    else:
                        save_session(sessionfile, filename, i + j)
                        print('URLError: exiting...')
                        raise QuitException()
            else:
                break
        print("Finished {} ({}/{})".format(
            name, i + j + 1, len(fields) + j))
    if os.path.isfile(sessionfile):
        os.remove(sessionfile)

class QuitException(Exception):
    pass

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
