=============
vocaran_tools
=============

Version 1.3

Dependencies
------------

`Python`_ 3 is required.  Python 2 is required for spynner and selenium
download methods.

.. _Python: http://www.python.org/download/

Speaking of which, `selenium`_ for Python 2 is required., as well as `spynner`_
for Python 2, for their respective download methods.

.. _selenium: http://pypi.python.org/pypi/selenium/
.. _spynner: https://github.com/makinacorpus/spynner

`Firefox`_ should also be installed for selenium download.

.. _Firefox: https://www.mozilla.org/en-US/firefox/new/

dl.py and move_songs.py depends on `stagger`_, a Python 3 package for
ID3v1/ID3v2 tag manipulation.

.. _stagger: http://pypi.python.org/pypi/stagger/0.4.2

move_songs.py additionally depends on `mp3info`_.  Download from the website or
use your distro's package manager.

.. _mp3info: http://www.ibiblio.org/mp3info/

test.py, containing the test suite for vocaran_tools.py, requires `md5sum`_, a
common utility.  On the off chance you don't have it, it's not necessary
anyway, unless you want to run the tests yourself.

.. _md5sum: https://en.wikipedia.org/wiki/Md5sum

Usage
-----

From the command line::

    vct
    vct add
    vct remove
    vct show
    vct tl
    vct dl
    vct move

Example:

Make a song list file ``list``::

    30::hello world!::artistP feat. miku::this album::comments

Add the file, noting the week of the Vocaran (vocaran_tools data is kept in
``$HOME/.vocaran_tools``.  Stored song lists are in ``songlists``)::

    vct add 113 list

Check added weeks::

    vct show

Translate the ranks::

    vct tl 113

Download your songs (Songs are downloaded to ``downloads``)::

    vct dl 113

Move them to your collection (Edit ``vocaran_tools/scripts/move_songs.py`` with
your music directory)::

    vct move
