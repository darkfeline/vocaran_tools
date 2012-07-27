#!/usr/bin/env python3

"""
dm.py

This module (data manager) contains constants and functions which can be used
to interact with vocaran_tools data files and directories.  Both
package-interior and package-exterior modules should use dm, instead of playing
with paths and files themselves.

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
