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

import stagger

# check dependencies
NULL = open(os.devnull, 'w')
try:
    subprocess.call(['mp3info'], stdout=NULL)
except OSError:
    raise Exception('move_songs.py depends on mp3info')

ROOT = "/home/darkfeline/Music/VOCALOID"
VOCALOIDS = ["初音ミク",
             ["鏡音リン・レン", "鏡音リン", "鏡音レン", "鏡音リンレン"],
             "巡音ルカ",
             "MEIKO",
             "KAITO",
             "GUMI",
             "Lily",
             "VY1",
             "VY2",
             "歌愛ユキ", 
             "猫村いろは",
             "重音テト",
             "空音ラナ",
             ["開発コード miki", "開発コードmiki", "miki"],
             ["神威がくぽ", "がくぽ"]
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

def process(file):
    # check file size for zero length files
    if os.path.getsize(file) < 500:
        print('File size is ' + os.path.getsize(file) + ' bytes. Skip? [y]/n ')
        i = input()
        if i.lower() in ['y', 'yes', '']:
            print('Skipping')
            return
        else:
            print('Continuing ({} may be corrupt)'.format(file)

    tag = stagger.read_tag(file)
    title = tag.title
    artist = tag.artist

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

    print("-" * 60)
    print("File: " + file)
    print("Title: " + title)
    print("Artist: " + artist)
    if not guess:
        print("Couldn't guess directory")
        for i, n in enumerate(VOCALOIDS):
            if isinstance(n, list):
                n = n[0]
            print(str(i) + " " + n)
        print("r base directory: " + ROOT)
        print("s skip")
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
            print("{} is a directory; skipping".format(os.path.join(newp, file)))
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
            print("""Old: 
Title:{title} 
Artist:{artist} 
Length:{length}
mtime:{mtime}""".format(title=title, artist=artist, length=length, mtime=mtime))

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
            print("""New: 
Title:{title} 
Artist:{artist} 
Length:{length}
mtime:{mtime}""".format(title=title, artist=artist, length=length, mtime=mtime))

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
