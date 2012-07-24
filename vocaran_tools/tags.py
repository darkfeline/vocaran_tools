#!/usr/bin/env python3

"""
tags.py

All things MP3-tag related.

"""

import os
import urllib.parse
import urllib.request
import urllib.error

import stagger
from stagger.id3 import *

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
