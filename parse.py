#!/usr/bin/env python3

import re

SEP = "::"

def srcparse(source):
    """Returns a dict with song rank keys mapped to corresponding NND IDs using
the html source from Vocaloidism.
    
The source should be the path to a file containing the html source of
the ranking section on the relevant Vocaloidism page.  srcparse scanes the
source and returns a dict where the key is a string which contains the rank
number of a song, with or without an 'h' prepended (the 'h' is present for
songs in the history section) or 'ed'.  The items each key refers to is a
string containing the NND ID (e.g. sm123456789 or nm123456789) of that song.

"""
    wvr = re.compile(r'#([0-9]+).*?www\.nicovideo\.jp/watch/([sn]m[0-9]+)', re.I)
    wvrhis = re.compile('THIS WEEK IN HISTORY', re.I)
    wvred = re.compile(r'ED Song.*?www\.nicovideo\.jp/watch/([sn]m[0-9]+)', re.I)
    links = {}
    switch = 0
    with open(source) as src:
        for line in src:
            # first scan line for song
            match = wvr.search(line)
            if match:
                a = match.group(1)
                if switch == 1:
                    # line is in history section, prepend number with 'h'.  If
                    # it's the last song (#1), go back to regular ranking
                    if a == "1":
                        switch = 2
                    a = 'h' + a
                links[a] = match.group(2)
                continue
            elif switch == 0:
                # if the line is not a song, check to see if the history
                # section is starting
                match = wvrhis.search(line)
                if match:
                    switch = 1
                    continue
            # check for ed song match
            match = wvred.search(line)
            if match:
                links['ed'] = match.group(1)
    return links

def lsparse(list, links):
    """Returns a list with all args needed to dl custom mp3 from nicomimi.
    
[
    [id, song_name, artist, album, comment, albumart],
    .
    .
    .
]

list is the name of a file with the following syntax: 
    Each line has 6 fields, separated with the globally defined string SEP.  The
    first field is either one of the keys in links generated from srcparse
    (i.e. rank number, with or without an 'h' prepended or 'ed') or a raw NND
    ID.  The rest of the fields are song name, artist, album, comment,
    albumart.
    e.g. rank_no|id::song_name::artist::album::comment::albumart

"""
    # regex magic follows
    sepm = r'(?:{})'.format(SEP)
    tail = sepm.join(r'(.*?)' for x in range(5))
    rank = re.compile(r'^(h?[0-9]+|ed)' + sepm + tail, re.I)
    idm = re.compile(r'^([sn]m[0-9]+)' + sepm + tail, re.I)
    s = re.compile(SEP)

    fields = []
    with open(list) as src:
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
                    file=list, line=line))
            fields.append([id, match.group(2), match.group(3), match.group(4),
                           match.group(5), match.group(6)][:len(c) + 1])
    return fields

def parse(list):
    """Returns a list with all args needed to dl custom mp3 from nicomimi.
    
[
    [id, song_name, artist, album, comment, albumart],
    .
    .
    .
]

list is the name of a file with the following syntax: 
    Each line has 6 fields, separated with the globally defined string SEP.  The
    first field is either one of the keys in links generated from srcparse
    (i.e. rank number, with or without an 'h' prepended or 'ed') or a raw NND
    ID.  The rest of the fields are song name, artist, album, comment,
    albumart.
    e.g. rank_no|id::song_name::artist::album::comment::albumart

"""
    # regex magic follows
    sepm = r'(?:{})'.format(SEP)
    tail = sepm.join(r'(.*?)' for x in range(5))
    idm = re.compile(r'^([sn]m[0-9]+)' + sepm + tail, re.I)
    s = re.compile(SEP)

    fields = []
    with open(list) as src:
        for line in src:
            c = s.findall(line)
            line = line.rstrip() + SEP * (5 - len(c))

            match = idm.search(line)
            if match:
                id = match.group(1).lower()
            fields.append([id, match.group(2), match.group(3), match.group(4),
                           match.group(5), match.group(6)][:len(c) + 1])
    return fields

def main(src, list, out):
    ranks = srcparse(src)
    fields = lsparse(list, ranks)

    with open(out, 'a') as f:
        for item in fields:
            line = ""
            for x in item:
                line += x
                line += SEP
            line = line[:len(line) - len(SEP)] # cut off final SEP
            line += '\n'
            f.write(line)

if __name__ == '__main__':
    import sys

    src = sys.argv[1]
    list = sys.argv[2]
    out = sys.argv[3]

    main(src, list, out)
