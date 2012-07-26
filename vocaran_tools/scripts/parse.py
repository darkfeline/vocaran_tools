#!/usr/bin/env python3

"""
parse.py

"""

from vocaran_tools.data import parse

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('rank_list_file')
    parser.add_argument('out_file')
    args = parser.parse_args(args)

    parse_main(args.source, args.rank_list_file, args.out_file)

def parse_main(source, list_file, out_file):

    import os
    import os.path

    from vocaran_tools.vocaloidism import get_vocaloidism

    if os.path.isfile(source):
        print('{} is a file; using as src'.format(source))
        src = source
    else:
        print('Getting Vocaloid HTML for week {}...'.format(source))
        source = int(source)
        src = 'src.tmp'
        get_vocaloidism(src, source)
    print('parsing src...')
    ranks = parse.parse_vocaloidism(src)
    print('checking parsed links...')
    if parse.checklinks(ranks):
        raise Exception('parse_vocaloidism links is incomplete.  Check src and/or \
                        parse_vocaloidism', parse.checklinks(ranks))
    if os.path.exists(out_file):
        if os.path.isfile(out_file):
            print('parsing original file...')
            fields1 = parse.read_list(out_file)
        else:
            raise Exception(out_file + ' is a directory.')
    print('parsing rank...')
    fields2 = parse.read_list(list_file, ranks=True)
    print('converting ranks...')
    fields2 = parse.convert_list(fields2, ranks)
    print('combining lists...')
    fields = fields1 + fields2
    print('writing to list_file...')
    parse.write_list(fields, out_file)
    if os.path.isfile('src.tmp'):
        print('removing src.tmp...')
        os.remove('src.tmp')
    print('Done.')

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
