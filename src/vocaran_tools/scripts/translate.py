"""
translate.py

"""

import os
import os.path

from vocaran_tools.data import parse
from vocaran_tools.data import dm
from vocaran_tools.vocaloidism import get_vocaloidism
from vocaran_tools.errors import FileFormatError

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('week', type=int)
    parser.add_argument('-s', '--source', action='store', type=str)
    args = parser.parse_args(args)

    translate_main(args.week, args.source)

def translate_main(week, source):
    if source is None:
        print('Getting Vocaloid HTML for week {}...'.format(str(week)))
        src = 'src.tmp'
        get_vocaloidism(src, week)
    else:
        print('Using {} as src'.format(source))
        src = source
    print('parsing src...')
    with open(src) as source:
        ranks = parse.parse_vocaloidism(source)
    print('checking parsed links...')
    if parse.checklinks(ranks):
        raise FileFormatError('parse_vocaloidism links is incomplete.  ' + 
            'Check source and/or parse_vocaloidism', parse.checklinks(ranks))
    print('reading song list data...')
    slist = dm.get_songlist(week)
    print('converting ranks...')
    parse.convert_list(slist, ranks)
    print('saving...')
    slist.save()
    if source is None and os.path.isfile('src.tmp'):
        print('removing src.tmp...')
        os.remove('src.tmp')
    print('Done.')

if __name__ == '__main__':
    import sys
    try:
        main(*sys.argv[1:])
    except FileFormatError as e:
        print(str(e))
        sys.exit(1)
