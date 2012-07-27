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

The program will provide additional usage information

Specifications
--------------

With version 1.3, file formats and data models have been completely revamped.
Specification information will be gradually migrated to their respective
modules.

File formats
````````````

All files are plain text.

With version 1.3, the old song list files are now merged.  Old song list files
implicitly contain rank information.

Song list files contain one song entry per line::

    song_entry ::= id SEP name [SEP artist [SEP album [SEP comment
                   [SEP apic]]]]
    SEP ::= '::'
    nndid ::= ('s' | 'n') ('m' | 'o') ('0' ... '9')+
    rank ::= ['h'] ('0' .. '9')+ | 'pkp' | 'ed'
    id ::= nndid | rank
    name ::= <any string that doesn't contain SEP>
    artist ::= <any string that doesn't contain SEP>
    album ::= <any string that doesn't contain SEP>
    comment ::= <any string that doesn't contain SEP>
    apic ::= 'none' | 'def' | <arbitrary set of strings of integers, e.g. '1',
             '2', '3' ...>

- SEP can be changed in parse.py.
- apic refers to albumart retrieved from nicomimi.net
- The ranks must correspond to a single weekly Vocaran's rankings.

With version 1.3, there is a new file type, currently called new song list
files.  It corresponds to SongList and RankedSongList data models, and is saved
and loaded by both.  RankedSongList can load all new song list files, but
SongList can only load ones without rank information.  Its file format will not
be explained in detail as manual editing won't be required.

Data models
```````````

Song rank dictionaries map rankings to NND ids.  They have the following
format::

    {'rank number':'sm123456789',
    'h5':'nm123456789',
    'pkp':'sm1',
    'ed':'sm2',
    '13':'sm3', ...
    }

With version 1.3, old song lists are deprecated by the new SongList and
RankedSongList classes.  See songlist.py for documentation.

Modules
-------

Module information will be gradually migrated to the corresponding modules.

Note: The following is out-of-date following package restructuring and
development of a curses user interface.  The dl.py, parse.py, and move_songs.py
scripts are now in vocaran_tools/scripts, while vocaran_tools.py will still
work as per the following.

dl.py
`````

dl.py facilitates bulk downloading of Nico Nico Douga (NND) songs through
nicomimi.net.  It no longer translates rank numbers into NNDIDs; this
functionality is now in parse.py.  Run dl.py from the command line::

    dl.py list

list is a song list file, containing the songs to download and relevant
information, one per line in the following format::

    id::song_name::artist::album::comment::albumart

- id is the NND id of the song.  Rank interpretation has been moved to
  parse.py.
- song_name (TIT2) will be used to tag the song; optional.
- artist (TPE1) will be used to tag the song; optional.
- album (TALB) will be used to tag the song; optional.
- comment (COMM) will be used to tag the song; optional.  Defaults to the NND
  id of the song.
- albumart (APIC) will be used to choose the attached picture.  Check the
  docstrings for tag() and getpic() in dl.py for more information.  Defaults to
  'smile'.

- The default field separator is '::', as it is unlikely to appear in the title
  of a song.  This can be changed, for now, by editing parse.py (dl.py uses
  parse.py for any parsing fuctions)::

    #SEP = "::"
    SEP = "@@"

dl functions
''''''''''''

dl.py contains various dl functions which are passed to dlloop to use to
download the songs.  Read the docstrings for the functions for details on each.

You can also write custom dl functions if you should need to.  dl function
names should start with dl, and take the same arguments as the base dl
function::

    def dl(file, id, title, artist, album='', comment='', apic='none'):

The function returns nothing, and has the end state of a file with the given
name created in the current directory which is the MP3 of the corresponding
video on Nico Nico Douga, and tagged accordingly.  

parse.py
````````

parse.py provides any parsing tools necessary for vocaran_tools.  It is also a
runnable script which processes rank information translation to NND id numbers.
It will fetch HTML from the Vocaloidism website given a week number.

Run parse.py from the command line::
    
    parse.py number list out

list is a song list file with ranks, formatted similarly to the input to dl.py,
but the id field can additionally be a rank number (1-150ish, depending on the
week), history rank number (h1-h5), pick-up (pkp) or ED (ed).  parse.py
translates the rank numbers to NND ids and appends the translated lines to out,
a growing song list file.

number can either be the week number, or the name of a file containing the HTML
source downloaded from the respective Vocaloidism page.

move_songs.py
`````````````

move_songs.py automates moving downloaded songs into your music directory.
Edit move_songs.py and change::
    
    ROOT = "/home/darkfeline/Music/VOCALOID"

to your own music directory.  The assumed directory structure is thus: songs
sung by a single VOCALOID are moved into their own subdirectory, and songs sung
by more than one VOCALOID are moved into the root directory.  move_songs.py
will parse each song's artist tag and select a destination directory, prompting
for confirmation.  If it cannot guess, it will prompt you to manually select a
directory.  

Additionally, move_songs.py will check for corrupt downloads (when the song is
less than a certain size), and prompt to skip.  These generally result from
when the song is not available via the selected dl function, yielding an html
error page instead of a valid mp3 file.

vocaran_tools.py
````````````````

This is currently just a wrapper script for the above modules.  Calling::

    vocaran_tools.py dl foo bar

is identical to:::

    dl.py foo bar

and 'parse' to parse.py, 'move' to move_songs.py.  Eventually, all of these
scripts will be moved to vocaran_tools.py.
