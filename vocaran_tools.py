#!/usr/bin/env python3

# vocaran_tools.py
# CLI script

import argparse

ACTIONS=(('-d', 'download'), 
         ('-p', 'parse')
        )

parser = argparse.ArgumentParser(description='vocaran_tools utility.')
parser.add_argument('args', nargs='*')
group = parser.add_mutually_exclusive_group(required=True)
for a, b in ACTIONS:
    group.add_argument(a, dest='action', action='store_const', const=b)
args = parser.parse_args()

if args.action == 'download':
    import dl
    dl.main(*args.args)
elif args.action == 'parse':
    import parse
    parse.main(*args.args)
