=============
vocaran_tools
=============

Windows tutorial
================

NOTE: I have stopped maintaining Windows support as of 2011-07-21.  That's not
to say vocaran_tools doesn't work on Windows, but the information provided in
the Windows section and any Windows tools and scripts are unmaintained as from
now.  Please refer to the Linux section for up-to-date documentation.

Installing
----------

Find, download and install the current version of `Python 3`_. Python is an
interpreted programming language.

.. _Python 3: http://www.python.org/about/

vocaran_tools is hosted on `github`_.  Download and extract the lastest version.

.. _github: https://github.com/darkfeline/vocaran_tools

You will also need `stagger`_ if you plan on using move_songs.py.  Download and
extract stagger into the vocaran_tools folder.  

.. _stagger: http://pypi.python.org/pypi/stagger/0.4.2

How to use
----------

dl.py
*****

Make two files in the vocaran_tools folder: src.txt and list.txt.  Be careful
with the file extensions: Windows may hide them from you.  If it just says src,
but it's a Text Document File or something similar, then the .txt extension is
hidden.  

In src.txt, put the HTML source code from Vocaloidism:

In Firefox:

1) Go to the Weekly Vocaloid Ranking page of the week you are doing.
2) Highlight all of the ranking information (All from #30 to the end of the ED
   Song)
3) Right-click > View Selection Source
4) Copy all of the source and paste into src.txt

In list.txt, put the songs and information, one song per line, like this::

    id::song_name::artist::album

Examples::

    29
    29::クルーキッド::
    29::クルーキッド::ヤオギ feat. 初音ミク
    29::クルーキッド::ヤオギ feat. 初音ミク::Vocaran song

Only the id is necessary.

::

    sm14258485::モノクロナイト::あーるP feat. 初音ミクsweet&dark
    h3::さよならメモリーズ::Ciel feat. GUMI
    ed::METROPOLIS CRISIS::MEIKO

You can use NND id (e.g., sm12345679), rank number, history rank number (e.g.,
h1, h2), or ed

Finally, run dl.bat to begin downloading.

Linux tutorial
==============

Dependencies
------------

move_songs.py depends on `stagger`_, a Python 3 package for ID3v1/ID3v2 tag
manipulation.

.. _stagger: http://pypi.python.org/pypi/stagger/0.4.2

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

parse.py
--------

parse.py provides any parsing tools necessary for vocaran_tools.  It is also a
runnable script which processes rank information translation to NND id numbers.

Run parse.py from the command line::
    
    parse.py src list out
