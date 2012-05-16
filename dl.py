#!/usr/bin/env python3

"""
dl.py

"""

import os
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import hashlib
import subprocess

import stagger
from stagger.id3 import *

def dl(file, id, title='', artist='', album='', comment='', apic='none'):
    """Request a custom MP3 from nicomimi.net

    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic() and tag() for information about apic.

    Replaced entirely by dl_nicomimi(), as that function is superior to this
    one in almost every single way.  This function will be kept for reference.

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

def dl_nicomimi(file, id, title='', artist='', album='', comment='',
        apic='none'):
    """Request an MP3 download from nicomimi.net, then tag using stagger.

    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic() and tag() for information about apic.

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

def dl_nicosound(file, id, title='', artist='', album='', comment='',
        apic='none'):
    """Download MP3 from nicosound using selenium, then tag using stagger.

    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic() and tag() for information about apic.

    """
    dir = os.path.dirname(__file__)
    selenium_path = os.path.join(dir, 'selenium_dl.py')
    return_code = subprocess.call([selenium_path, id, file])
    if return_code != 0:
        raise FileNotAvailableException()
    tag(file, id, title, artist, album, comment, apic)

def tag(file, id, title='', artist='', album='', comment='', apic='none'):
    """Tag the MP3 file using stagger.  
    
    comment is tagged as COMM, as opposed to USLT that nicomimi.net custom uses
    for comments/lyrics.  
    
    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic for information about apic.  Additionally, if apic
    is 'none', no picture is tagged.
    
    """
    t = stagger.default_tag()
    t._filename = file
    t[TIT2] = title
    t[TPE1] = artist
    t[TALB] = album
    t[USLT] = USLT(text=comment)
    if apic != 'none':
        getpic(file + '.jpg', id, apic)
        t[APIC] = APIC(file + '.jpg')
        os.remove(file + '.jpg')
    t.write()

def getpic(file, id, apic):
    """Get albumart and save to file

    apic can be the following:

        The following use nicomimi.net servers.

        'def' default art
        '1', '2', ... arbitrary albumart for song (there may either be none or
            more than 5, depending on song)

        The following uses smilevideo.jp servers.

        'smile' default icon

    Returns 0 if everything went okay, and 1 if something went wrong.

    """
    if apic == 'none':
        return 0
    elif apic == 'def' or is_int(apic):
        if is_int(apic):
            id = id + '?aw=' + int(apic)
        conn = urllib.request.urlopen(
                'http://www.nicomimi.net/thumbnail/{}'.format(id))
        data = conn.read()
        conn.close()
    elif apic == 'smile':
        conn = urllib.request.urlopen(
                'http://tn-skr4.smilevideo.jp/smile?i={}'.format(id[2:]))
        data = conn.read()
        conn.close()
    else:
        return 1
    with open(file, 'wb') as f:
        f.write(data)
    return 0


def is_int(string):
    """Return True if string is string of int and False otherwise.

    >>>is_int('one')
    False
    >>>is_int('15')
    True

    """
    try:
        int(string)
        return True
    except ValueError:
        return False

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
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', dest='force', action='store_true', default=False)
    parser.add_argument('-m', '--method', dest='method', action='store',
            choices=('dl_nicomimi', 'dl_nicosound'), default='dl_nicosound')
    parser.add_argument('file')
    args = parser.parse_args(args)

    try:
        this = sys.modules[__name__]
        dlmain(args.file, this.__dict__[args.method], args.force)
    except QuitException:
        sys.exit()

def dlmain(filename, dlf, *args):

    """Parse song list file and pass on to dlloop

    filename is name of song list file.
    dlf is dl function to use.
    args is passed directly to dlloop().

    dlmain() also handles some personal defaults.  In particular:
    Comment fields are set to id if blank.
    apic are set to 'smile' if blank.

    """

    import parse

    print('Parsing file...')
    fields = parse.parse_list(filename)
    # personal defaults here
    for x in fields:
        if x[4] == '':
            x[4] = x[0]
        if x[5] == '':
            x[5] = 'smile'
    print('Downloading...')
    try:
        dlloop(dlf, fields, filename, *args)
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
    if os.path.isfile(sessionfile):
        print('Loading last session...')
        j = load_session(sessionfile, filename)
        if j < 0:
            print("Data file checksum differs from file; ignoring session")
            j = 0
    else:
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
            except FileNotAvailableException:
                print('File not available; skipping...')
                break
            else:
                break
        print("Finished {} ({}/{})".format(
            name, i + j + 1, len(fields) + j))
    if os.path.isfile(sessionfile):
        os.remove(sessionfile)


class QuitException(Exception):
    pass

class FileNotAvailableException(Exception):
    pass


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
