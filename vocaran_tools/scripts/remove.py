#!/usr/bin/env python3

"""
remove.py

"""

import os

from vocaran_tools.data import dm
from vocaran_tools.errors import StructureException, FileFormatError
from vocaran_tools.errors import ExitException

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('week')
    args = parser.parse_args(args)

    remove_main(args.week)

def remove_main(week):
    try:
        slist = dm.get_songlist(week)
    except (StructureException, FileFormatError) as e:
        print(str(e))
        raise ExitException(1)
    os.remove(slist.file)

if __name__ == '__main__':
    import sys
    try:
        main(*sys.argv[1:])
    except ExitException as e:
        sys.exit(e.code)
