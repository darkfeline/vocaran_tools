"""
dm.py

This module (data manager) contains constants and functions which can be used
to interact with vocaran_tools data files and directories.  Both
package-interior and package-exterior modules should use dm, instead of playing
with paths and files themselves.

File formats
------------

All files are plain text.

With version 1.3, the old song list files are now merged.  Old song list files
implicitly contain rank information.

Old song list files contain one song entry per line::

    song_entry ::= id SEP name [SEP artist [SEP album [SEP comment
                   [SEP apic]]]]
    SEP ::= '::'
    nndid ::= ('s' | 'n') ('m' | 'o') ('0' ... '9')+
    rank ::= ['h'] ('0' .. '9')+ | 'pkp' | 'ed'
    id ::= nndid | rank
    name ::= <any string that doesn't contain SEP>
    artist ::= <any string that doesn't contain SEP>
    album ::= <any string that doesn't contain SEP>
    comment ::= <any string that doesn't contain SEP>
    apic ::= 'none' | 'smile' | 'def' | <arbitrary set of strings of integers,
             e.g. '1', '2', '3' ...>

- SEP can be changed in parse.py.
- apic refers to albumart retrieved from nicomimi.net
- The ranks must correspond to a single weekly Vocaran's rankings.

Or in English::

    id::song_name::artist::album::comment::albumart

- id is the NND id of the song.  Rank interpretation has been moved to
  parse.py.
- song_name (TIT2) will be used to tag the song; optional.
- artist (TPE1) will be used to tag the song; optional.
- album (TALB) will be used to tag the song; optional.
- comment (COMM) will be used to tag the song; optional.  Defaults to the NND
  id of the song.
- albumart (APIC) will be used to choose the attached picture.  Check the
  docstrings for tag() and getpic() in dl.py for more information.  Defaults to
  'smile'.

- The default field separator is '::', as it is unlikely to appear in the title
  of a song.  This can be changed, for now, by editing parse.py (dl.py uses
  parse.py for any parsing fuctions)::

    #SEP = "::"
    SEP = "@@"

With version 1.3, there is a new file type, currently called new song list
files.  It corresponds to SongList and RankedSongList data models, and is saved
and loaded by both.  RankedSongList can load all new song list files, but
SongList can only load ones without rank information.  Refer to songlist.py for
details on the file format.

Data models
-----------

Song rank dictionaries map rankings to NND ids.  They have the following
format::

    {'rank number':'sm123456789',
    'h5':'nm123456789',
    'pkp':'sm1',
    'ed':'sm2',
    '13':'sm3', ...
    }

With version 1.3, old song lists are deprecated by the new SongList and
RankedSongList classes.  See songlist.py for documentation.

"""

import os
import os.path

from vocaran_tools.errors import StructureError
from vocaran_tools.data import songlist

DATA_DIR = os.path.join(os.environ['HOME'], '.vocaran_tools')
SONGLIST_DIR = os.path.join(DATA_DIR, 'songlists')
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'downloads')
SESSION_FILE = os.path.join(DATA_DIR, 'session')

def init_dirs():
    """Initiate data directories."""
    mkdir(DATA_DIR)
    mkdir(SONGLIST_DIR)
    mkdir(DOWNLOAD_DIR)

def mkdir(path):

    """Safely make directory

    Ignores if directory already exists, but raises StructureError if a file
    with the same name exists.

    """

    if os.path.isfile(path):
        raise StructureError('Could not make directory.')
    if not os.path.isdir(path):
        os.mkdir(path)

def make_songlist(week, overwrite=False):
    """Make a new SongList associated with its path and week"""
    path = get_songlist_path(week)
    if not overwrite and os.path.isfile(path):
        raise StructureError(
                '{} already exists and overwrite is False.'.format(path))
    l = songlist.SongList(path, week)
    return l

def make_rankedsonglist(week, overwrite=False):
    """Make a new RankedSongList associated with its path and week"""
    path = get_songlist_path(week)
    if not overwrite and os.path.isfile(path):
        raise StructureError(
                '{} already exists and overwrite is False.'.format(path))
    l = songlist.RankedSongList(path, week)
    return l

def check_songlists():
    """Return a sorted list of songlist files"""
    x = os.listdir(SONGLIST_DIR)
    x.sort()
    return x

def get_songlist_path(week):

    """Return the path of songlist file of given week

    Note that file may or may not exist.

    """

    return os.path.join(SONGLIST_DIR, str(week))

def get_songlist(week):
    """Return corresponding SongList or RankedSongList"""
    path = get_songlist_path(week)
    if not os.path.isfile(path):
        raise StructureError('{} is not a file.'.format(path))
    try:
        slist = songlist.SongList.load(path)
    except TypeError:
        slist = songlist.RankedSongList.load(path)
    return slist
