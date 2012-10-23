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
import subprocess

from vocaran_tools import tags
from vocaran_tools.errors import FileNotAvailableError


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
