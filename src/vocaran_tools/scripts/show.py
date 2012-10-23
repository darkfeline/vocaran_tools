import os

from vocaran_tools.data import dm
from vocaran_tools.errors import StructureError, ExitException


def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--raw', action='store_true', default=False)
    parser.add_argument('name', nargs='?', type=int, default=None)
    args = parser.parse_args(args)

    try:
        show_main(args.name, raw=args.raw)
    except StructureError as e:
        print(str(e))
        raise ExitException(1)


def print_header(slist):
    print("{}, {} entries".format(slist.name, len(slist)), end="")
    if slist.done:
        print(", Done", end="")
    print()


def show_main(name, raw=False):
    if name is None:
        for x in dm.check_songlists():
            x = dm.get_songlist(x)
            print_header(x)
    else:
        x = dm.get_songlist(name)  # raises StructureError
        if raw:
            path = dm.get_songlist_path(name)
            with open(path) as f:
                for line in f:
                    print(line, end="")
        else:
            print_header(x)
            for entry in x:
                print('-' * 10)
                print(_entry_template.format(*iter(entry))
_entry_template = """ID:{}
Name:{}
Artist:{}
Album:{}
Comment:{}
APIC:{}"""

if __name__ == '__main__':
    import sys
    try:
        main(*sys.argv[1:])
    except ExitException as e:
        sys.exit(e.code)
