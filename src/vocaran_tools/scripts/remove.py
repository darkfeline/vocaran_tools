"""
remove.py

"""

import os

from vocaran_tools.data import dm
from vocaran_tools.errors import ExitException


def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    args = parser.parse_args(args)

    os.remove(dm.get_songlist_path(args.name))

if __name__ == '__main__':
    import sys
    try:
        main(*sys.argv[1:])
    except ExitException as e:
        sys.exit(e.code)
