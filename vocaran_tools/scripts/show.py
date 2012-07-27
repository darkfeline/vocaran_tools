#!/usr/bin/env python3

"""
show.py

"""

from vocaran_tools.data import dm

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args(args)

    show_main()

def show_main():
    for x in dm.check_songlists:
        x = dm.get_songlist(x)
        print("{}, {}, {} entries".format(x.week, x.__class__, len(x)))

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
