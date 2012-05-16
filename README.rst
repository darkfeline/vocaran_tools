=============
vocaran_tools
=============

Dependencies
------------

Both `Python`_ 3 and Python 2 are needed.  While vocaran_tools is primarily a
Python 3 library, it relies on selenium for browser automation to download from
nicosound.anyap.info, and selenium is currently Python 2 only.

.. _Python: http://www.python.org/download/

Speaking of which, `selenium`_ is required for Python 2.

.. _selenium: http://pypi.python.org/pypi/selenium/

`Firefox`_ should also be installed.

.. _Firefox: https://www.mozilla.org/en-US/firefox/new/

dl.py and move_songs.py depends on `stagger`_, a Python 3 package for
ID3v1/ID3v2 tag manipulation.

.. _stagger: http://pypi.python.org/pypi/stagger/0.4.2

move_songs.py additionally depends on `mp3info`_.  Download from the website or
use your distro's package manager.

.. _mp3info: http://www.ibiblio.org/mp3info/

Specifications
--------------

File formats
````````````

All files are plain text.

Song list files contain one song entry per line::

    song_entry ::= NND_id SEP song_name [SEP artist [SEP album [SEP comment
                   [SEP apic]]]]
    SEP ::= '::'
    NND_id ::= ('s' | 'n') ('m' | 'o') ('0' ... '9')+
    song_name ::= <any string that doesn't contain SEP>
    artist ::= <any string that doesn't contain SEP>
    album ::= <any string that doesn't contain SEP>
    comment ::= <any string that doesn't contain SEP>
    apic ::= 'none' | 'def' | <arbitrary set of strings of integers, e.g. '1',
             '2', '3' ...>

- SEP can be changed in parse.py.
- apic refers to albumart retrieved from nicomimi.net

Song list files with ranks also take ranks in song entries::

    song_entry_with_ranks ::= NND_id_with_rank SEP song_name [SEP artist [SEP
                              album [SEP comment [SEP albumart]]]]
    NND_id_with_rank ::= NND_id | ['h'] ('0' .. '9')+ | 'pkp' | 'ed'

- The ranks must correspond to a single weekly Vocaran's rankings.
- Where song list files with ranks are allowed, "with ranks" must be explicitly
  stated.

Data models
```````````

Song rank dictionaries map rankings to NND ids.  They have the following
format::

    {'rank number':'sm123456789',
    'h5':'nm123456789',
    'pkp':'sm1',
    'ed':'sm2',
    '13',:sm3', ...
    }

Song lists are list representations of song list files.  They have the
following format::

    [[id, song_name, artist, album, comment, apic], ... ]

- There are also song lists with ranks that represent song list files with
  ranks.
- Where song lists with ranks are allowed, "with ranks" must be explicitly
  stated.

Modules
-------

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
