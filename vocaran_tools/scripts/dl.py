#!/usr/bin/env python3

"""
dl.py

"""

import os
import urllib.parse
import urllib.error
import hashlib

from vocaran_tools.errors import QuitException, FileNotAvailableException

def load_session(sessionfile, filename):
    """Return the index from session file after checking md5sum.
    
    If the md5sum doesn't match, return -1.
    
    """
    with open(sessionfile) as f:
        hash = f.readline().rstrip()
        i = int(f.readline().rstrip())
    with open(filename) as g:
        if (hashlib.sha256(
            ''.join(g.readlines()[:i+1]).rstrip().encode('UTF-8')
            ).hexdigest() == hash):
            return i
    return -1

def save_session(sessionfile, filename, i):
    """Save index to sessionfile with md5sum of song list file up to index."""
    with open(sessionfile, 'w') as f:
        with open(filename) as g:
            f.write(hashlib.sha256(
                ''.join(g.readlines()[:i+1]).rstrip().encode('UTF-8')
                ).hexdigest())
            f.write('\n')
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
        from vocaran_tools import dl
        dlmain(args.file, dl.__dict__[args.method], args.force)
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

    from vocaran_tools.data import parse

    print('Parsing file...')
    fields = parse.read_list(filename)
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
                print('File not available; writing dummy file...')
                break
            else:
                break
        print("Finished {} ({}/{})".format(
            name, i + j + 1, len(fields) + j))
    if os.path.isfile(sessionfile):
        os.remove(sessionfile)


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
