"""
dm.py

This module (data manager) contains constants and functions which can be used
to interact with vocaran_tools data files and directories.  Both
package-interior and package-exterior modules should use dm, instead of playing
with paths and files themselves.

File formats
############

All files are plain text.

There is one file type, currently called song list files.  It corresponds to
the SongList data model.  Refer to songlist.py for details.

Data models
###########

Currently, the only data model is the SongList

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


def make_songlist(name, overwrite=False):
    """Make a new SongList"""
    path = get_songlist_path(name)
    if not overwrite and os.path.exists(path):
        raise StructureError(
            '{} already exists and overwrite is False.'.format(path))
    l = songlist.SongList(path)
    return l


def check_songlists():
    """Return a sorted list of songlist files"""
    x = os.listdir(SONGLIST_DIR)
    x.sort()
    return x


def get_songlist_path(name):
    """Return the path of songlist file with given name

    Note that file may or may not exist.

    """
    return os.path.join(SONGLIST_DIR, str(name))


def get_songlist(name):
    """Return SongList"""
    path = get_songlist_path(name)
    if not os.path.isfile(path):
        raise StructureError('{} is not a file.'.format(path))
    slist = songlist.SongList.load(path)
    return slist
