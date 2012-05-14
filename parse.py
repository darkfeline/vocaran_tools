#!/usr/bin/env python3

import re

SEP = "::"
NNDID = '[sn][mo][0-9]+'

def parse_vocaloidism(source):
    """Return a dict with song ranks from Vocaloidism.
    
    source should be the path to a file containing the html source of the
    relevant Vocaloidism weekly ranking page.  parse_vocaloidism() scans the
    source and returns a dict with the following format:

    {'rank number':'sm123456789',
    'h5':'nm123456789',
    'pkp':'sm1',
    'ed':'sm2',
    '13',:sm3', ...
    }

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
            # check for pickup song match
            if wvrpkp.search(line):
                match = wvrpkp.search(line)
                links['pkp'] = match.group(1)
            # check for ed song match
            elif wvred.search(line):
                match = wvred.search(line)
                links['ed'] = match.group(1)
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
                links[a] = match.group(2)
            # check for start of history section
            elif switch == 0:
                match = wvrhis.search(line)
                if match:
                    switch = 1
    return links

def checklinks(links):
    """Check the return value of parse_vocaloidism() for completeness.

    Return a set of expected keys that are missing.  Expected keys are '1' to
    '30', 'h1' to 'h5', 'pkp' and 'ed'.
    
    """
    given = set(links)
    expected = set([str(i) for i in range(1,31)] + 
                   ['h{}'.format(i) for i in range(1,6)] + ['pkp', 'ed'])
    return expected - given

def convert_list(lst, links):
    """Convert the song list with ranks into an argument list.

    Return a list with the following format:
    [[id, song_name, artist, album, comment, albumart], ... ]

    lst is the name of a file with the following syntax, with default SEP '::':
    id::song_name[::artist[::album[::comment[::albumart]]]]
    id ~= [sn][mo][0-9]+|h?[0-9]+|pkp|ed

    links is the list returned by parse_vocaloidism()

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

def parse_list(lst):
    """Parse a song list with ids into an argument list.
    
    [[id, song_name, artist, album, comment, albumart], ... ]

    lst is the name of a file with the following syntax, with default SEP '::':
    id::song_name[::artist[::album[::comment[::albumart]]]]
    id ~= [sn][mo][0-9]+|h?[0-9]+|pkp|ed

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
        dl.get_vocaloidism(src, number)
    print('parsing src...')
    ranks = parse_vocaloidism(src)
    print('checking parsed links...')
    if checklinks(ranks):
        raise Exception('parse_vocaloidism links is incomplete.  Check src and/or \
                        parse_vocaloidism', checklinks(ranks))
    print('parsing rank...')
    fields = convert_list(lst, ranks)
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
