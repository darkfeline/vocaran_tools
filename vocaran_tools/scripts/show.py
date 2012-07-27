#!/usr/bin/env python3

"""
show.py

"""

import os

from vocaran_tools.data import dm
from vocaran_tools.errors import StructureException, ExitException

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--raw', action='store_true', default=False)
    parser.add_argument('week', nargs='?', type=int, default=None)
    args = parser.parse_args(args)

    try:
        show_main(args.week, raw=args.raw)
    except StructureException as e:
        print(str(e))
        raise ExitException(1)

def show_main(week, raw=False):
    if week is None:
        for x in dm.check_songlists():
            x = dm.get_songlist(x)
            print("{}, {}, {} entries".format(x.week, x.__class__.__name__, 
                len(x)))
    else:
        path = dm.get_songlist_path(week)
        if not os.path.isfile(path):
            raise StructureException('{} is not a file.'.format(path))
        if raw:
            with open(path) as f:
                for line in f:
                    print(line, end="")
        else:
            x = dm.get_songlist(week)
            print("{}, {}, {} entries".format(x.week, x.__class__.__name__,
                len(x)))
            for entry in x:
                print('-' * 10)
                print(
"""ID:{}
Name:{}
Artist:{}
Album:{}
Comment:{}
APIC:{}""".format(*iter(entry)))

if __name__ == '__main__':
    import sys
    try:
        main(*sys.argv[1:])
    except ExitException as e:
        sys.exit(e.code)
