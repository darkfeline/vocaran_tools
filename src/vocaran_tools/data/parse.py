"""
parse.py

This module handles some parsing and especially parsing old-style song list
files, translating them into SongList and RankedSongList objects.

"""

import re

from vocaran_tools.data import songlist
from vocaran_tools.errors import FileFormatError

SEP = "::"
NNDID = '[sn][mo][0-9]+'

def parse_vocaloidism(source):
    """Return a song rank dict parsed from Vocaloidism ranking page.

    source should be a file object containing the html source

    """
    wvr = re.compile(r'<strong>.*?([0-9]+).*?www\.nicovideo\.jp/watch/' +
                     '({})'.format(NNDID), re.I)
    wvrhis = re.compile('THIS WEEK IN HISTORY', re.I)
    wvrpkp = re.compile(r'<strong>.*pick.*?www\.nicovideo\.jp/watch/' +
                        '({})'.format(NNDID), re.I)
    wvred = re.compile(r'ED Song.*?www\.nicovideo\.jp/watch/' +
                       '({})'.format(NNDID), re.I)
    song_ranks = {}
    switch = 0
    for line in source:
        # check for pickup song match
        if wvrpkp.search(line):
            match = wvrpkp.search(line)
            song_ranks['pkp'] = match.group(1)
        # check for ed song match
        elif wvred.search(line):
            match = wvred.search(line)
            song_ranks['ed'] = match.group(1)
        # scan line for song
        elif wvr.search(line):
            match = wvr.search(line)
            a = match.group(1)
            # history
            if switch == 1:
                # line is in history section, prepend number with 'h'.  If
                # it's the last song (#1), go back to regular ranking
                if a == "1":
                    switch = 2
                a = 'h' + a
            song_ranks[a] = match.group(2)
        # check for start of history section
        elif switch == 0:
            match = wvrhis.search(line)
            if match:
                switch = 1
    return song_ranks

def parse_ofuro(source):
    """Return a song rank dict parsed from Ofurotaimu ranking page.

    source should be a file object containing the html source

    """
    pat = re.compile(
            r'<br />([0-9]+). <b><a href="http://www.nicovideo.jp/watch/' +
            '({})'.format(NNDID)
    )
    song_ranks = {}
    for line in source:
        # check for song
        if pat.search(line):
            match = pat.search(line)
            song_ranks[match.group(1)] = match.group(2)
    return song_ranks

def checklinks(song_ranks):
    """Check the song rank dict for completeness.

    Return a set of expected keys that are missing.  Expected keys are '1' to
    '30', 'h1' to 'h5', 'pkp' and 'ed'.
    
    """
    given = set(song_ranks)
    expected = set([str(i) for i in range(1,31)] + 
                   ['h{}'.format(i) for i in range(1,6)] + ['pkp', 'ed'])
    return expected - given

def convert_list(slist, song_ranks):
    """Convert the song list with ranks into a song list."""
    rank = re.compile(r'h?[0-9]+|ed|pkp', re.I)
    for entry in slist:
        if rank.match(entry.id):
            entry.id = song_ranks[entry.id.lower()]

def read_list(filename, ranks=False):

    """Parse a song list file and return a song list.
    
    If ranks is True, then read_list() will treat the file as a song list file
    with ranks and return a song list with ranks.
    
    """

    if ranks == True:
        slist = songlist.RankedSongList()
    else:
        slist = songlist.SongList()

    # regex magic follows
    sep = r'(?:{})'.format(SEP)
    rank = ''
    if ranks == True:
        rank = r'|h?[0-9]+|ed|pkp'
    idp = re.compile(sep.join([r'^(?P<id>{})'.format(NNDID + rank),
        r'(?P<title>.*?)', r'(?P<artist>.*?)', r'(?P<album>.*?)',
        r'(?P<comment>.*?)', r'(?P<apic>.*?)']), re.I) 
    s = re.compile(SEP)

    with open(filename) as src:
        for line in src:
            # pad out SEPs
            c = s.findall(line)
            line = line.rstrip() + SEP * (5 - len(c))
            match = idp.search(line)
            if match:
                g = match.group
                slist.add(g('id'), g('title'), g('artist'), g('album'),
                               g('comment'), g('apic'))
            else:
                raise FileFormatError(
                    "Error when parsing {file}: {line}".format(
                        file=filename, line=line))
    return slist
