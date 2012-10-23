"""
tags.py

All things MP3-tag related.

"""

import os
import urllib.parse
import urllib.request
import urllib.error

import stagger
from stagger import id3


def atag(file, id, apic='none', **kwargs):
    """Download albumart then pass to tag()

    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic for information about apic.  Additionally, if apic
    is 'none', no picture is tagged.

    """
    if apic != 'none':
        pic = file + '.jpg'
        getpic(pic, id, apic)
    else:
        pic = None
    tag(file, picture=pic, **kwargs)
    if pic:
        os.remove(pic)


def tag(file, title='', artist='', album='', comment='', picture=None,
        composer='', lyricist='', lyrics='', bpm='', key='', languages='',
        length='', orig_artist='', orig_album=''):
    """Tag MP3 file using stagger"""
    t = stagger.default_tag()
    t._filename = file
    if title:
        t[id3.TIT2] = title
    if artist:
        t[id3.TPE] = artist
    if album:
        t[id3.TALB] = album
    if comment:
        t[id3.COMM] = comment
    if picture:
        t[id3.APIC] = id3.APIC(picture)
    if composer:
        t[id3.TCOM] = composer
    if lyricist:
        t[id3.TEXT] = lyricist
    if lyrics:
        t[id3.USLT] = id3.USLT(text=lyrics)
    if bpm:
        t[id3.TBPM] = bpm
    if key:
        t[id3.TKEY] = key
    if languages:
        t[id3.TLAN] = languages
    if length:
        t[id3.TLEN] = length
    if orig_artist:
        t[id3.TOPE] = orig_artist
    if orig_album:
        t[id3.TOAL] = orig_album
    t.write()


def getpic(file, id, apic):
    """Get albumart and save to file

    apic can be the following:

        - The following use nicomimi.net servers.

            - 'def' default art
            - '1', '2', ... arbitrary albumart for song (there may either be
              none or more than 5, depending on song)

        - The following uses smilevideo.jp servers.

            - 'smile' default icon

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
