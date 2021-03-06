#!/usr/bin/env python3

"""
move_songs.py

move_songs.py automates moving downloaded songs into your music directory.
Change::

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

"""

import os
import os.path
import re
import shutil
import time
import subprocess

import stagger

from vocaran_tools.data import dm
from vocaran_tools.errors import DependencyError

# check dependencies
NULL = open(os.devnull, 'w')
try:
    subprocess.call(['mp3info'], stdout=NULL)
except OSError:
    raise DependencyError('move_songs.py depends on mp3info')

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
             ["SF-A2 開発コード miki", "開発コードmiki", "miki"],
             ["神威がくぽ", "がくぽ"],
             "氷山キヨテル",
             ["IA -ARIA ON THE PLANETES-", "IA"],
             "CUL",
             "結月ゆかり",
             "歌手音ピコ",
             "リング・スズネ",
             "蒼姫ラピス",
             "結月ゆかり",
             "Mew"
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

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args(args)

    move_main()

def move_main():
    """Find all MP3s in current directory by extension and run process() on
    each one."""
    os.chdir(dm.DOWNLOAD_DIR)
    dir = os.listdir()
    p = re.compile(r".*\.mp3$", re.I)
    dir = [f for f in dir if p.match(f)]
    for f in dir:
        process(f)

def process(file):

    """Move file interactively."""

    # check file size for zero length files
    if os.path.getsize(file) < 500:
        print('File size is ' + str(os.path.getsize(file)) + 
              ' bytes. Skip?  [Y/n] ')
        i = input()
        if i.lower() in ['y', 'yes', '']:
            print('Skipping')
            return
        else:
            print('Continuing ({} may be corrupt)'.format(file))

    tag = stagger.read_tag(file)
    title = tag.title
    artist = tag.artist
    print("-" * 60)
    print("File: " + file)
    print("Title: " + title)
    print("Artist: " + artist)

    # guess file (in guess)
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
    elif len(imatch) > 1:
        guess = ""
    else:
        guess = None

    oldp = os.path.join(os.getcwd(), file)
    # loop for input
    while True:
        if guess == None:
            print("Couldn't guess directory")
            i = input("[S/c/t]? ").lower()
            if i == "":
                print("Skipping")
                break
        else:
            newp = os.path.join(ROOT, guess)
            print("From: " + oldp)
            print("To: " + newp)
            i = input("[Y/n/c/t]? ").lower()
            if i in ("y", ""):
                move(oldp, newp, file)
                break
            elif i == "n":
                print("Skipping")
                break
        if i == "c":
            for i, n in enumerate(VOCALOIDS):
                if isinstance(n, list):
                    n = n[0]
                print(str(i) + " " + n)
            print("r base directory: " + ROOT)
            print("c cancel")
            i = input("destination?")
            if i.lower() == "r":
                guess = ""
            elif i.lower() == "c":
                print("Canceling")
                continue
            else:
                i = int(i)
                if not 0 <= i < len(VOCALOIDS):
                    print(i + ": Not a valid input: Canceling")
                    continue
                guess = VOCALOIDS[i]
                # For synonymous vocaloid names, use first element in list
                if isinstance(guess, list):
                    guess = guess[0]
        elif i == "t":
            print("Manually type directory")
            guess = input(ROOT + "/")

def move(oldp, newp, file):

    print()
    if os.path.isdir(os.path.join(newp, file)):
        print("{} is a directory; skipping".format(os.path.join(newp,
                                                                file)))
        return 1
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
        template = "Title:{title}\nArtist:{artist}\nLength:{length}\
                \nmtime:{mtime}"
        print("Old:\n" + template.format(title=title, artist=artist,
            length=length, mtime=mtime))

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
        print("New:\n" + template.format(title=title, artist=artist,
            length=length, mtime=mtime))

        i = input("[y/N]? ").lower()
        if i in ("y", "yes"):
            os.rename(oldp, os.path.join(newp, file))
            print("Overwritten")
            return 0
        else:
            print("Skipping")
            return 1
    else:
        shutil.move(oldp, newp)
        print("Moved")
        return 0

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
