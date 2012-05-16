#!/usr/bin/env python3

"""
vocaran_tools.py
CLI script

"""

if __name__ == "__main__":

    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', action='store', choices=('dl',
        'parse', 'move'))
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()

    if args.action == 'dl':
        import dl
        sys.argv[0] = 'dl.py'
        dl.main(*args.args)
    elif args.action == 'parse':
        import parse
        sys.argv[0] = 'parse.py'
        parse.main(*args.args)
    elif args.action == 'move':
        import move_songs
        sys.argv[0] = 'move_songs.py'
        move_songs.main(*args.args)
