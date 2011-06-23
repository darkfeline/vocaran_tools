#!/usr/bin/env python3

# Distributed under GPLv3.  The full license can be found here:
# http://www.gnu.org/licenses/gpl.html

import re
import urllib.parse
import urllib.request
import urllib.error

def srcparse(source):
    """Returns a dict listing of song ranks and NND IDs.
    
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

def lsparse(list, links, sep='::'):
    """Returns a list with all args needed to dl custom mp3 from nicomimi.
    
[
    [id, song_name, artist, album, comment, albumart],
    .
    .
    .
]

list is the name of a file with the following syntax: 
    Each line has 6 fields, separated with the string given to lsparse.  The
    first field is either one of the keys in links generated from srcparse
    (i.e. rank number, with or without an 'h' prepended or 'ed') or a raw NND
    ID.  The rest of the fields are song name, artist, album, comment,
    albumart.
    e.g. rank_no|id::song_name::artist::album::comment::albumart

"""
    # regex magic follows
    sepm = r'(?:{})'.format(sep)
    tail = sepm.join(r'(.*?)' for x in range(5))
    rank = re.compile(r'^(h?[0-9]+|ed)' + sepm + tail, re.I)
    idm = re.compile(r'^([sn]m[0-9]+)' + sepm + tail, re.I)
    s = re.compile(sep)

    fields = []
    with open(list) as src:
        for line in src:
            c = s.findall(line)
            line = line.rstrip() + sep * (5 - len(c))
            match = rank.search(line)
            if match:
                id = links[match.group(1).lower()]
            else:
                match = idm.search(line)
                if match:
                    id = match.group(1).lower()
            fields.append([id, match.group(2), match.group(3), match.group(4),
                           match.group(5), match.group(6)][:len(c) + 1])
    return fields

def dl(file, id, title, artist, album='', comment='', apic='def'):
    """Requests custom .mp3 from nicomimi.net

file should probably match name and end in '.mp3' as the right extension.
apic can be 'none' (no albumart), 'def' (default art), and an arbitrary number
of string depending on the song, thus: '1', '2', '3'  It's probably better to
either stick with 'def' or 'none'.

"""
    params = urllib.parse.urlencode({'vid' : id,
                                     'access_key1' : 'hePj8S3ewMayA',
                                     'access_key2' : '13jsAnxfaKEE6',
                                     'APIC' : apic,
                                     'TIT2' : title,
                                     'TPE1' : artist,
                                     'TALB' : album,
                                     'USLT' : comment})
    params = params.encode('utf-8')
    try:
        conn = urllib.request.urlopen(
            'http://media1.nicomimi.net/customplay.rb', params)
    except urllib.error.HTTPError:
        print('-' * 60)
        print('Failed for ' + file)
        print('id: ' + id)
        print('title: ' + title)
        print('artist: ' + artist)
        print('album: ' + album)
        print('comment: ' + comment)
        print('apic: ' + apic)
        return
    data = conn.read()
    with open(file, 'wb') as f:
        f.write(data)
    conn.close()
    print('Finished ' + file)

def dlloop(fields):
    """fields returned from lsparse."""
    a = re.compile(r'/')
    for x in fields:
        name = x[1] + '.mp3'
        name = a.sub('|', name)
        dl(name, *x)

if __name__ == '__main__':
    import sys
    
    src = sys.argv[1]
    list = sys.argv[2]
    links = srcparse(src)
    fields = lsparse(list, links)
    # set comment field to id
    for x in fields:
        if len(x) < 5:
            for i in range(4 - len(x)):
                x.append('')
            x.append(x[0])
    dlloop(fields)
