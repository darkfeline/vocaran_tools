"""
dl.py

This module holds dl functions and wrapper functions for Python 2 download
methods.

dl functions
------------

dl.py contains various dl functions which are passed to dlloop to use to
download the songs.  Read the docstrings for the functions for details on each.

You can also write custom dl functions if you should need to.  dl function
names should start with dl, and take the same arguments as the base dl
function::

    def dl(file, id, title, artist, album='', comment='', apic='none'):

The function returns nothing, and has the end state of a file with the given
name created in the current directory which is the MP3 of the corresponding
video on Nico Nico Douga, and tagged accordingly.


"""

import os
import urllib.parse
import urllib.request
import http.cookiejar
import subprocess

from vocaran_tools import tags
from vocaran_tools.errors import FileNotAvailableError

def dl(file, id, title='', artist='', album='', comment='', apic='none'):
    """Deprecated.

    Request a custom MP3 from nicomimi.net

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
    """Deprecated.

    Request an MP3 download from nicomimi.net, then tag using stagger.

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
    tags.atag(file, id, title, artist, album, comment, apic)

def dl_nicosound_selenium(file, id, title='', artist='', album='', comment='',
        apic='none'):
    """Download MP3 from nicosound using selenium, then tag using stagger.

    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic() and tag() for information about apic.

    """
    dir = os.path.dirname(__file__)
    selenium_path = os.path.join(dir, 'selenium_dl.py')
    return_code = subprocess.call([selenium_path, id, file])
    if return_code != 0:
        raise FileNotAvailableError()
    tags.atag(file, id, title, artist, album, comment, apic)

def dl_nicosound_spynner(file, id, title='', artist='', album='', comment='',
        apic='none'):
    """Download MP3 from nicosound using spynner, then tag using stagger.

    file should probably match the title and end in '.mp3' as the right
    extension.  See getpic() and tag() for information about apic.

    """
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'spynner_dl.py')
    with open(os.devnull, 'wb') as f:
        return_code = subprocess.call([path, id, file], stdout=f, stderr=f)
    if return_code != 0:
        raise FileNotAvailableError()
    tags.atag(file, id, title, artist, album, comment, apic)
