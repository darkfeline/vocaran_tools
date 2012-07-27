#!/usr/bin/env python3

import os
import os.path

from vocaran_tools.errors import StructureError
from vocaran_tools.data import songlist

DATA_DIR = os.path.join(os.environ['HOME'], '.vocaran_tools')
SONGLIST_DIR = os.path.join(DATA_DIR, 'songlists')
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'downloads')
SESSION_FILE = os.path.join(DATA_DIR, 'session')

def init_dirs():
    mkdir(DATA_DIR)
    mkdir(SONGLIST_DIR)
    mkdir(DOWNLOAD_DIR)

def mkdir(path):
    if os.path.isfile(path):
        raise StructureError('Could not make directory.')
    if not os.path.isdir(path):
        os.mkdir(path)

def make_rankedsonglist(week, overwrite=False):
    path = get_songlist_path(week)
    if not overwrite and os.path.isfile(path):
        raise StructureError(
                '{} already exists and overwrite is False.'.format(path))
    l = songlist.RankedSongList(path, week)
    return l

def check_songlists():
    x = os.listdir(SONGLIST_DIR)
    x.sort()
    return x

def get_songlist_path(week):
    return os.path.join(SONGLIST_DIR, str(week))

def get_songlist(week):
    path = get_songlist_path(week)
    if not os.path.isfile(path):
        raise StructureError('{} is not a file.'.format(path))
    try:
        slist = songlist.SongList.load(path)
    except TypeError:
        slist = songlist.RankedSongList.load(path)
    return slist
