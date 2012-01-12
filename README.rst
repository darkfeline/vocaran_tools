=============
vocaran_tools
=============

Dependencies
------------

dl.py and move_songs.py depends on `stagger`_, a Python 3 package for
ID3v1/ID3v2 tag manipulation.

.. _stagger: http://pypi.python.org/pypi/stagger/0.4.2

move_songs.py additionally depends on `mp3info`_.  Download from the website or
use your distro's package manager.

.. _mp3info: http://www.ibiblio.org/mp3info/

dl.py
-----

dl.py facilitates bulk downloading of Nico Nico Douga (NND) songs through
nicomimi.net.  It can match weekly Vocaran rank numbers to the respective
song's NND id using the HTML source from the respective Vocaloidism page.  Run
dl.py from the command line::

    dl.py list

list is a file containing the songs to download and relevant information, one
per line in the following format::

    id::song_name::artist::album::comment::albumart

- id is the NND id of the song.  Rank interpretation has been moved to
  parse.py.
- song_name (TIT2) will be used to tag the song; optional.
- artist (TPE1) will be used to tag the song; optional.
- album (TALB) will be used to tag the song; optional.
- comment (COMM) will be used to tag the song; optional.  The tag
  nicomimi uses for this is the ID3v2 lyrics tag USLT, NOT the ID3v2 comments
  tag COMM.  However, now that dl.py uses altdl() instead of dl(), comments are
  tagged to COMM.  Defaults to the NND id of the song.
- albumart (APIC) will be used to choose the attached picture.
  Valid values are 'none', 'def', '1', '2', et cetera.  While 'none' (no album
  art) and 'def' (default album art) are guaranteed, any numbered art (1, 2,
  3...) and how many numbered art are available are NOT guaranteed.  Although
  now dl.py uses altdl() to download and tag MP3s, the script will still grab
  pictures from the same location on nicomimi.net servers.  Defaults to 'def'.

- The default field separator is '::', as it is unlikely to appear in the title
  of a song.  This can be changed, for now, by editing parse.py (dl.py uses
  parse.py for any parsing fuctions)::

    #SEP = "::"
    SEP = "@@"

dl functions
````````````

dl.py contains various dl functions which are passed to dlloop to use to
download the songs.  Read the docstrings for the functions for details on each.

You can also write custom dl functions if you should need to.  dl function
names should start with dl, and take the same arguments as the base dl
function::

    def dl(file, id, title, artist, album='', comment='', apic='def'):

The function returns nothing, and has the end state of a file with the given
name created in the current directory which is the MP3 of the corresponding
video on Nico Nico Douga, and tagged accordingly.  

parse.py
--------

parse.py provides any parsing tools necessary for vocaran_tools.  It is also a
runnable script which processes rank information translation to NND id numbers.
It will fetch HTML from the Vocaloidism website given a week number.

Run parse.py from the command line::
    
    parse.py number list out

list is formatted similarly to the input to dl.py, but the id field can
additionally be a rank number (1-176), history rank number (h1-h5), pick-up
(pkp) or ED (ed).  parse.py appends the lines to out, translating rank numbers
and such into NND ids.
