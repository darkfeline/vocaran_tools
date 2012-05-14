#!/usr/bin/env python3

# vocaran_tools.py
# CLI script

import argparse

ACTIONS=(('-d', 'download', 'download songs'),
         ('-c', 'convert', 'convert song list ranks'),
         ('-m', 'move', 'move songs')
        )

parser = argparse.ArgumentParser(description='vocaran_tools utility.')
parser.add_argument('args', nargs='*')
group = parser.add_mutually_exclusive_group(required=True)
for a, b, c in ACTIONS:
    group.add_argument(a, dest='action', action='store_const', const=b, help=c)
args = parser.parse_args()

if args.action == 'download':
    import dl
    dl.main(*args.args)
elif args.action == 'convert':
    import parse
    parse.main(*args.args)
elif args.action == 'move':
    import move_songs
    move_songs.main()
