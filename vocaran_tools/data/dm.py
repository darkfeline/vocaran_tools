#!/usr/bin/env python3

import os
import os.path

from vocaran_tools.errors import StructureException
from vocaran_tools.data import songlist
from vocaran_tools import data

DATA_DIR = os.path.join(os.environ['HOME'], '.vocaran_tools')
SONGLIST_DIR = os.path.join(DATA_DIR, 'songlists')
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'downloads')

def init_dirs():
    mkdir(DATA_DIR)
    mkdir(SONGLIST_DIR)
    mkdir(DOWNLOAD_DIR)

def mkdir(path):
    if os.path.isfile(path):
        raise StructureException('Could not make directory.')
    if not os.path.isdir(path):
        os.mkdir(path)

def make_rankedsonglist(week, overwrite=False):
    path = os.path.join(SONGLIST_DIR, str(week))
    if not overwrite and os.path.isfile(path):
        raise StructureException(
                '{} already exists and overwrite is False.'.format(path))
    l = songlist.RankedSongList(week)
    l.file = path
    return l

def check_songlists():
    x = os.listdir(SONGLIST_DIR)
    x.sort()
    return x

def get_songlist(week):
    path = os.path.join(SONGLIST_DIR, str(week))
    if not os.path.isfile(path):
        raise StructureException('{} is not a file.'.format(path))
    l = data.load(path)
    return l