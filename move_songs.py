#!/usr/bin/env python3

# move_songs.py
# 
# moves vocaloid songs according to artist tag


import os
import os.path
import re
import subprocess

import stagger

ROOT = "/home/darkfeline/Music/VOCALOID"
_VOCALOIDS = ["初音ミク",
             ["鏡音リン・レン", "鏡音リン", "鏡音レン"],
             "巡音ルカ",
             "MEIKO",
             "KAITO",
             "GUMI",
             "Lily"
             "VY1",
             "歌愛ユキ", 
             "猫村いろは"]
VOCALOIDS = []
for a in _VOCALOIDS:
    if isinstance(a, list):
        x = []
        for b in a:
            x.append(re.compile(b))
        VOCALOIDS.append(x)
    else:
        VOCALOIDS.append(re.compile(a))

def main():
    dir = os.listdir(os.getcwd())
    p = re.compile(r".*\.mp3$", re.I)
    dir = [f for f in dir if p.match(f)]
    for f in dir:
        process(f)

def process(file):
    tag = stagger.read_tag(file)
    title = tag.title
    artist = tag.artist

    imatch = []
    for i, p in enumerate(VOCALOIDS):
        if isinstance(p, list):
            for q in p:
                if q.search(artist):
                    imatch.append(i)
                    break
        else:
            if p.search(artist):
                imatch.append(i)

    if len(imatch) == 1:
        guess = _VOCALOIDS[imatch[0]]
    else:
        guess = None

    print("-" * 60)
    print("File: " + file)
    print("Title: " + title)
    print("Artist: " + artist)
    if not guess:
        print("Couldn't guess directory")
        for i, n in enumerate(_VOCALOIDS):
            if isinstance(n, list):
                n = n[0]
            print(str(i) + " " + n)
        print("r base directory: " + ROOT)
        i = input("destination?")
        if i.lower() == "r":
            guess = ""
        else:
            i = int(i)
            if not 0 <= i < len(_VOCALOIDS):
                print(i + ": Not a valid input: Skipping")
                return
            guess = _VOCALOIDS[i]

    oldp = os.path.join(os.getcwd(), file)
    newp = os.path.join(ROOT, guess)

    print(oldp + " -> " + newp)
    i = input("y/n[y]? ").lower()
    if i in ("y", "yes", ""):
        subprocess.call(["mv", oldp, newp])
        print("Moved")
    else:
        return

if __name__ == '__main__':
    main()
