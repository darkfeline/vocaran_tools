#!/usr/bin/env python3

"""
dl.py

"""

import os
import urllib.parse
import urllib.request
import http.cookiejar
import subprocess

from vocaran_tools import tags
from vocaran_tools.errors import FileNotAvailableException

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
    tags.tag(file, id, title, artist, album, comment, apic)

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
    tags.tag(file, id, title, artist, album, comment, apic)
