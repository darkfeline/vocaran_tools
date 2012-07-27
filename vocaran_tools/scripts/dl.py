#!/usr/bin/env python3

"""
dl.py

"""

import os
import urllib.parse
import urllib.error
import hashlib

from vocaran_tools.errors import ExitException, FileNotAvailableError
from vocaran_tools.errors import StructureError
from vocaran_tools import dl
from vocaran_tools.data import dm, songlist

def load_session(sessionfile, filename):
    """Return the index from session file after checking md5sum.
    
    If the md5sum doesn't match, return -1.
    
    """
    with open(sessionfile) as f:
        hash = f.readline().rstrip()
        i = int(f.readline().rstrip())
    with open(filename) as g:
        if (hashlib.sha256(''.join(g.readlines()).rstrip().encode('UTF-8')
            ).hexdigest() == hash):
            return i
    return -1

def save_session(sessionfile, filename, i):
    """Save index to sessionfile with md5sum of song list file."""
    with open(sessionfile, 'w') as f:
        with open(filename) as g:
            f.write(hashlib.sha256(''.join(
                g.readlines()).rstrip().encode('UTF-8')).hexdigest())
            f.write('\n')
            f.write(str(i))

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', dest='force', action='store_true', default=False)
    parser.add_argument('-m', '--method', dest='method', action='store',
            choices=('dl_nicomimi', 'dl_nicosound_selenium',
                'dl_nicosound_spynner'), default='dl_nicosound_spynner')
    parser.add_argument('week', type=int)
    args = parser.parse_args(args)

    dlmain(args.week, dl.__dict__[args.method], args.force)

def dlmain(week, dlf, *args):

    """Parse song list file and pass on to dlloop

    filename is name of song list file.
    dlf is dl function to use.
    args is passed directly to dlloop().

    dlmain() also handles some personal defaults.  In particular:
    Comment fields are set to id if blank.
    apic are set to 'smile' if blank.

    """

    print('Loading song list...')
    slist = dm.get_songlist(week)
    if isinstance(slist, songlist.RankedSongList):
        print('Translate song list first')
        raise ExitException(1)
    # personal defaults here
    for entry in slist:
        if entry.comment == '':
            entry.comment = entry.id
        if entry.apic == '':
            entry.apic = 'smile'
    print('Downloading...')
    dlloop(dlf, slist, dm.get_songlist_path(week), *args)
    print('Marking song list as done...')
    slist.done = True
    slist.save()
    print('Done.')

def dlloop(dlf, slist, path, force=False):

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

    try:
        rejects = dm.get_songlist(0)
    except StructureError:
        rejects = dm.make_songlist(0)

    sessionfile= dm.SESSION_FILE
    # load session
    if os.path.isfile(sessionfile):
        print('Loading last session...')
        j = load_session(sessionfile, path)
        if j < 0:
            print("Data file checksum differs from file; ignoring session")
            j = 0
    else:
        j = 0
    for i, entry in enumerate(slist):
        if i < j:
            continue
        bname = re_illegal.sub('|', entry.name) + '.mp3'
        name = os.path.join(dm.DOWNLOAD_DIR, bname)
        print("Fetching {} ({}/{})".format(bname, i + 1, len(slist)))
        while True:
            try:
                dlf(name, *entry)
            except KeyboardInterrupt as e:
                print('Writing current session...')
                save_session(sessionfile, path, i - 1)
                rejects.save()
                raise ExitException(0)
            except urllib.error.URLError as e:
                if re_error.search(str(e)):
                    if force:
                        print('URLError: retrying...')
                        continue
                    else:
                        save_session(sessionfile, path, i - 1)
                        rejects.save()
                        print('URLError: exiting...')
                        raise ExitException(1)
            except FileNotAvailableError:
                print('File not available; adding to rejects...')
                if slist.week != 0:
                    rejects.add(entry)
                break
            else:
                break
        print("Finished {} ({}/{})".format(bname, i + 1, len(slist)))
        rejects.save()

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
