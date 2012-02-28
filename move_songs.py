#!/usr/bin/env python3

# move_songs.py
# 
# moves vocaloid songs according to artist tag


import os
import os.path
import re
import shutil
import time
import subprocess
import itertools

import stagger

# check dependencies
NULL = open(os.devnull, 'w')
try:
    subprocess.call(['mp3info'], stdout=NULL)
except OSError:
    raise Exception('move_songs.py depends on mp3info')

ROOT = "/home/darkfeline/Music/VOCALOID"
VOCALOIDS = [["初音ミク", "ミク"],
             ["鏡音リン・レン", "鏡音レン・リン", "鏡音リン", "鏡音レン",
              "鏡音リンレン", "リン", "レン"],
             ["巡音ルカ", "ルカ"],
             ["MEIKO", "Meiko", "メイコ"],
             ["KAITO", "Kaito", "カイト"],
             "GUMI", 
             "Lily",
             "VY1",
             "VY2",
             "歌愛ユキ", 
             "猫村いろは",
             "重音テト",
             "空音ラナ",
             ["開発コード miki", "開発コードmiki", "miki"],
             ["神威がくぽ", "がくぽ"],
             "氷山キヨテル",
             ["IA -ARIA ON THE PLANETES-", "IA"],
             "CUL",
             "結月ゆかり",
             "歌手音ピコ"
            ]
PVOCALOIDS = []
for a in VOCALOIDS:
    if isinstance(a, list):
        x = []
        for b in a:
            x.append(re.compile(b))
        PVOCALOIDS.append(x)
    else:
        PVOCALOIDS.append(re.compile(a))

def main():
    """Finds all MP3s in current directory by extension and runs process() on
    each."""
    dir = os.listdir(os.getcwd())
    p = re.compile(r".*\.mp3$", re.I)
    dir = [f for f in dir if p.match(f)]
    for f in dir:
        process(f)

def print_vocaloid_prompt():
    """Pretty prints vocaloid choice prompt"""
    # Make string list
    x = []
    for i, n in enumerate(VOCALOIDS):
        if isinstance(n, list):
            n = n[0]
        x.append(str(i) + " " + n)
    # Find optimum # of cols
    max_width = 60
    cols = 1
    while sum(col_width(x, cols)) + cols <= max_width:
        cols += 1
    cols -= 1 # we went over one in while loop
    widths = col_width(x, cols)
    # split list into rows
    x = make_col(x, cols) # vert, column-wise
    x = itertools.zip_longest(*x, fillvalue="") # make row-wise
    # build print template
    temp = ""
    for i in range(cols):
        temp += "{{{0}:{1}}}".format(i, widths[i])
        temp += '|'
    temp = temp[:-1]  # drop last separator
    for row in x:
        print(temp.format(*row))

    print("r base directory: " + ROOT)
    print("s skip")

def make_col(x, cols, vert=True):
    """Returns a list with list x split into some number of columns, with
    entries going vertically (succeeding values in column) or horizontally
    (succeeding values going across columns)."""
    if vert:
        base_height = len(x) // cols
        extra_height = len(x) % cols
        y = []
        a = 0
        for i in range(cols):
            b = a + base_height
            if extra_height > 0:
                b += 1
                extra_height -= 1
            y.append(x[a:b])
            a = b
    else:
        y = [x[a:a + cols] for a in range(0, len(x), cols)]  # row-wise, horiz
    return y

def col_width(x, cols, vert=True):
    """Returns a list of the column widths if a tuple of strings is split into
    some number of columns going vertically (succeeding values in column) or
    horizontally (succeeding values going across columns)."""
    y = make_col(x, cols, vert)
    widths = []
    for col in y:
        widths.append(len(max(col, key=len)))
    return widths

def process(file):
    tag = stagger.read_tag(file)
    title = tag.title
    artist = tag.artist
    print("-" * 60)
    print("File: " + file)
    print("Title: " + title)
    print("Artist: " + artist)

    # check file size for zero length files
    if os.path.getsize(file) < 500:
        print('File size is ' + str(os.path.getsize(file)) + 
              ' bytes. Skip?  [y]/n ')
        i = input()
        if i.lower() in ['y', 'yes', '']:
            print('Skipping')
            return
        else:
            print('Continuing ({} may be corrupt)'.format(file))

    imatch = []
    for i, p in enumerate(PVOCALOIDS):
        if isinstance(p, list):
            for q in p:
                if q.search(artist):
                    imatch.append(i)
                    break
        else:
            if p.search(artist):
                imatch.append(i)

    if len(imatch) == 1:
        guess = VOCALOIDS[imatch[0]]
        # For synonymous vocaloid names, use first element in list
        if isinstance(guess, list):
            guess = guess[0]
    else:
        guess = None

    if not guess:
        print("Couldn't guess directory")
        print_vocaloid_prompt()
        i = input("destination?")
        if i.lower() == "r":
            guess = ""
        elif i.lower() == "s":
            print("Skipping")
            return
        else:
            i = int(i)
            if not 0 <= i < len(VOCALOIDS):
                print(i + ": Not a valid input: Skipping")
                return
            guess = VOCALOIDS[i]
            # For synonymous vocaloid names, use first element in list
            if isinstance(guess, list):
                guess = guess[0]

    oldp = os.path.join(os.getcwd(), file)
    newp = os.path.join(ROOT, guess)

    print("From: " + oldp)
    print("To: " + newp)
    i = input("[y]/n? ").lower()
    if i in ("y", "yes", ""):
        # Deal with if file already exists
        print()
        if os.path.isdir(os.path.join(newp, file)):
            print("{} is a directory; skipping".format(os.path.join(newp,
                                                                    file)))
        elif os.path.isfile(os.path.join(newp, file)):
            print("{} exists. Replace?".format(os.path.join(newp, file)))

            tag = stagger.read_tag(os.path.join(newp, file))
            title = tag.title
            artist = tag.artist
            length = int(subprocess.check_output(['mp3info', '-p', '%S',
                                                  os.path.join(newp, file)]))
            length = '{:02}:{:02}:{:02}'.format(
                length // 3600, length % 3600 // 60, length % 3600 % 60)
            length = length.lstrip('0:')
            mtime = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                      time.gmtime(os.path.getmtime(os.path.join(newp, file))))
            template = "Old:\nTitle:{title}\nArtist:{artist}\nLength:{length}\
                    \nmtime:{mtime}"
            print(template.format(title=title, artist=artist, length=length,
                                  mtime=mtime))

            tag = stagger.read_tag(oldp)
            title = tag.title
            artist = tag.artist
            length = int(subprocess.check_output(['mp3info', '-p', '%S',
                                                  oldp]))
            length = '{:02}:{:02}:{:02}'.format(
                length // 3600, length % 3600 // 60, length % 3600 % 60)
            length = length.lstrip('0:')
            mtime = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                      time.gmtime(os.path.getmtime(oldp)))
            print(template.format(title=title, artist=artist, length=length,
                                  mtime=mtime))

            i = input("[y]/n? ").lower()
            if i in ("y", "yes", ""):
                os.rename(oldp, os.path.join(newp, file))
                print("Overwritten")
            else:
                print("Skipping")
                return
        else:
            shutil.move(oldp, newp)
            print("Moved")
    else:
        print("Skipping")
        return

if __name__ == '__main__':
    main()
