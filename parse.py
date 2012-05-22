#!/usr/bin/env python3

"""
parse.py

"""

import re

SEP = "::"
NNDID = '[sn][mo][0-9]+'

def parse_vocaloidism(source):
    """Return a song rank dict parsed from Vocaloidism ranking page.
    
    source should be the path to a file containing the html source of the
    relevant Vocaloidism weekly ranking page.

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
    with open(source) as src:
        for line in src:
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

def checklinks(song_ranks):
    """Check the song rank dict for completeness.

    Return a set of expected keys that are missing.  Expected keys are '1' to
    '30', 'h1' to 'h5', 'pkp' and 'ed'.
    
    """
    given = set(song_ranks)
    expected = set([str(i) for i in range(1,31)] + 
                   ['h{}'.format(i) for i in range(1,6)] + ['pkp', 'ed'])
    return expected - given

def convert_list(fields, song_ranks):
    """Convert the song list with ranks into a song list."""
    rank = re.compile(r'h?[0-9]+|ed|pkp', re.I)
    for entry in fields:
        if rank.match(entry[0]):
            entry[0] = song_ranks[entry[0].lower()]
    return fields

def read_list(filename, ranks=False):

    """Parse a song list file and return a song list.
    
    If ranks is True, then read_list() will treat the file as a song list file
    with ranks and return a song list with ranks.
    
    """

    # regex magic follows
    sep = r'(?:{})'.format(SEP)
    rank = ''
    if ranks == True:
        rank = r'|h?[0-9]+|ed|pkp'
    idp = re.compile(sep.join([r'^(?P<id>{})'.format(NNDID + rank),
        r'(?P<title>.*?)', r'(?P<artist>.*?)', r'(?P<album>.*?)',
        r'(?P<comment>.*?)', r'(?P<albumart>.*?)']), re.I) 
    s = re.compile(SEP)

    fields = []
    with open(filename) as src:
        for line in src:
            # pad out SEPs
            c = s.findall(line)
            line = line.rstrip() + SEP * (5 - len(c))
            match = idp.search(line)
            if match:
                g = match.group
                fields.append([g('id'), g('title'), g('artist'), g('album'),
                               g('comment'), g('albumart')])
            else:
                raise Exception("Error when parsing {file}: {line}".format(
                    file=filename, line=line))
    return fields

def write_list(fields, filename):
    """Writes a song list to a song list file."""
    with open(filename, 'w') as f:
        for item in fields:
            line = ""
            for x in item:
                line += x
                line += SEP
            line = line[:len(line) - len(SEP)] # cut off final SEP
            line += '\n'
            f.write(line)

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('rank_list_file')
    parser.add_argument('out_file')
    args = parser.parse_args(args)

    parse_main(args.source, args.rank_list_file, args.out_file)

def parse_main(source, list_file, out_file):

    import os
    import os.path
    import dl

    if os.path.isfile(source):
        print('{} is a file; using as src'.format(source))
        src = source
    else:
        print('Getting Vocaloid HTML for week {}...'.format(source))
        source = int(source)
        src = 'src.tmp'
        dl.get_vocaloidism(src, source)
    print('parsing src...')
    ranks = parse_vocaloidism(src)
    print('checking parsed links...')
    if checklinks(ranks):
        raise Exception('parse_vocaloidism links is incomplete.  Check src and/or \
                        parse_vocaloidism', checklinks(ranks))
    if os.path.exists(out_file):
        if os.path.isfile(out_file):
            print('parsing original file...')
            fields1 = read_list(out_file)
        else:
            raise Exception(out_file + ' is a directory.')
    print('parsing rank...')
    fields2 = read_list(list_file, ranks=True)
    print('converting ranks...')
    fields2 = convert_list(fields2, ranks)
    print('combining lists...')
    fields = fields1 + fields2
    print('writing to list_file...')
    write_list(fields, out_file)
    if os.path.isfile('src.tmp'):
        print('removing src.tmp...')
        os.remove('src.tmp')
    print('Done.')

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
