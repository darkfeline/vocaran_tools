#!/usr/bin/env python3

import re

SEP = "::"
NNDID = '[sn][mo][0-9]+'

def srcparse(source):
    """Returns a dict with song rank keys mapped to corresponding NND IDs using
the html source from Vocaloidism.
    
The source should be the path to a file containing the html source of
the ranking section on the relevant Vocaloidism page.  srcparse scanes the
source and returns a dict where the key is a string which contains the rank
number of a song, with or without an 'h' prepended (the 'h' is present for
songs in the history section), 'pkp' or 'ed'.  The items each key refers to is a
string containing the NND ID (e.g. sm123456789 or nm123456789) of that song.

"""
    wvr = re.compile(r'<strong>.*?([0-9]+).*?www\.nicovideo\.jp/watch/' +
                     '({})'.format(NNDID), re.I)
    wvrhis = re.compile('THIS WEEK IN HISTORY', re.I)
    wvrpkp = re.compile(r'<strong>.*pick.*?www\.nicovideo\.jp/watch/' +
                        '({})'.format(NNDID), re.I)
    wvred = re.compile(r'ED Song.*?www\.nicovideo\.jp/watch/' +
                       '({})'.format(NNDID), re.I)
    links = {}
    switch = 0
    with open(source) as src:
        for line in src:
            # first scan line for song
            if wvr.search(line):
                match = wvr.search(line)
                a = match.group(1)
                # history
                if switch == 1:
                    # line is in history section, prepend number with 'h'.  If
                    # it's the last song (#1), go back to regular ranking
                    if a == "1":
                        switch = 2
                    a = 'h' + a
                links[a] = match.group(2)
            # check for pickup song match
            elif wvrpkp.search(line):
                match = wvrpkp.search(line)
                links['pkp'] = match.group(1)
            # check for ed song match
            elif wvred.search(line):
                match = wvred.search(line)
                links['ed'] = match.group(1)
            # check for history
            elif switch == 0:
                # if the line is not a song, check to see if the history
                # section is starting
                match = wvrhis.search(line)
                if match:
                    switch = 1
    return links

def checklinks(links):
    """Checks if the links returned from srcparse() is complete or not.
Returns a set of expected keys that are missing."""
    given = set(links)
    expected = set([str(i) for i in range(1,31)] + 
                   ['h{}'.format(i) for i in range(1,6)] + ['pkp', 'ed'])
    return expected - given

def lsparse(lst, links):
    """Returns a list with all args needed to dl custom mp3 from nicomimi.
    
[
    [id, song_name, artist, album, comment, albumart],
    .
    .
    .
]

lst is the name of a file with the following syntax: 
    Each line has 6 fields, separated with the globally defined string SEP.
    The first field is either one of the keys in links generated from srcparse
    (i.e. rank number, with or without an 'h' prepended, 'pkp' or 'ed') or a
    raw NND ID.  The rest of the fields are song name, artist, album, comment,
    albumart.
    e.g. rank_no|id::song_name::artist::album::comment::albumart

links is the return list from srcparse()

"""
    # regex magic follows
    sepm = r'(?:{})'.format(SEP)
    tail = sepm.join(r'(.*?)' for x in range(5))
    rank = re.compile(r'^(h?[0-9]+|ed|pkp)' + sepm + tail, re.I)
    idm = re.compile(r'^({})'.format(NNDID) + sepm + tail, re.I)
    s = re.compile(SEP)

    fields = []
    with open(lst) as src:
        for line in src:
            c = s.findall(line)
            line = line.rstrip() + SEP * (5 - len(c))
            match = rank.search(line)
            if match:
                id = links[match.group(1).lower()]
            else:
                match = idm.search(line)
                if match:
                    id = match.group(1).lower()
            if not match:
                raise Exception("Error when parsing {file}: {line}".format(
                    file=lst, line=line))
            fields.append([id, match.group(2), match.group(3), match.group(4),
                           match.group(5), match.group(6)][:len(c) + 1])
    return fields

def parse(lst):
    """Returns a list with all args needed to dl custom mp3 from nicomimi.
    
[
    [id, song_name, artist, album, comment, albumart],
    .
    .
    .
]

lst is the name of a file with the following syntax: 
    Each line has 6 fields, separated with the globally defined string SEP.  The
    first field is either one of the keys in links generated from srcparse
    (i.e. rank number, with or without an 'h' prepended or 'ed') or a raw NND
    ID.  The rest of the fields are song name, artist, album, comment,
    albumart.
    e.g. id::song_name::artist::album::comment::albumart

"""
    # regex magic follows
    sep = r'(?:{})'.format(SEP)
    idp = re.compile(sep.join([r'^(?P<id>{})'.format(NNDID), r'(?P<title>.*?)',
                               r'(?P<artist>.*?)', r'(?P<album>.*?)',
                               r'(?P<comment>.*?)', r'(?P<albumart>.*?)']),
                     re.I) 
    s = re.compile(SEP)

    fields = []
    with open(lst) as src:
        for line in src:
            c = s.findall(line) # number of SEPs in line
            line = line.rstrip() + SEP * (5 - len(c))

            match = idp.search(line)
            if match:
                g = match.group
                fields.append([g('id'), g('title'), g('artist'), g('album'),
                               g('comment'), g('albumart')][:len(c) + 1])
    return fields

def main(number, lst, out):
    import os
    import dl

    if os.path.isfile(number):
        print('{} is a file; using as src'.format(number))
        src = number
    else:
        print('Getting Vocaloid HTML for week {}...'.format(number))
        number = int(number)
        src = 'src.tmp'
        dl.getsrc(src, number)
    print('parsing src...')
    ranks = srcparse(src)
    print('checking parsed links...')
    if checklinks(ranks):
        raise Exception('srcparse links is incomplete.  Check src and/or \
                        srcparse', checklinks(ranks))
    print('parsing rank...')
    fields = lsparse(lst, ranks)
    print('appending to lst...')
    with open(out, 'a') as f:
        for item in fields:
            line = ""
            for x in item:
                line += x
                line += SEP
            line = line[:len(line) - len(SEP)] # cut off final SEP
            line += '\n'
            f.write(line)
    if os.path.isfile('src.tmp'):
        print('removing src.tmp...')
        os.remove('src.tmp')
    print('Done.')

if __name__ == '__main__':
    import sys

    number = sys.argv[1]
    lst = sys.argv[2]
    out = sys.argv[3]

    main(number, lst, out)
