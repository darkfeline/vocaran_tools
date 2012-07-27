#!/usr/bin/env python3

"""
add.py

"""

from vocaran_tools.data import dm, parse
from vocaran_tools.errors import StructureError, FileFormatError
from vocaran_tools.errors import ExitException

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('week')
    parser.add_argument('file')
    args = parser.parse_args(args)

    add_main(args.week, args.file)

def add_main(week, file):
    try:
        slist = parse.read_list(file, ranks=True)
    except (StructureError, FileFormatError) as e:
        print(str(e))
        raise ExitException(1)
    slist.file = dm.get_songlist_path(week)
    slist.week = week
    slist.save()

if __name__ == '__main__':
    import sys
    try:
        main(*sys.argv[1:])
    except ExitException as e:
        sys.exit(e.code)
