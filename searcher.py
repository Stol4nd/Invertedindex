import sys
import argparse
from init import init,  check_dir
from add import add


def command_check(parsed_query, root_dir):
    if not check_dir(root_dir):
        print(f'error: directory {root_dir} is not initialized as searching directory')
        sys.exit(1)
    if parsed_query.command == 'add':
        add(root_dir, parsed_query.files)
    elif parsed_query.command == "info":
        print("(no extra parameters)")
    else:
        for i, w in enumerate(parsed_query.words, start=1):
            print(f"word {i}: {w}")
        print(f"limit: {parsed_query.limit}")


def main(argv):
    if argv.count('--root') == 0:
        print('error: parametr --root is required')
        sys.exit(1)
    if argv.count('--root') > 1:
        print('error: parametr --root specified multiple times')
        sys.exit(1)

    root_index = argv.index('--root')
    try:
        root_dir = argv[root_index + 1]
    except IndexError:
        print('error: --root command requires a value')
        sys.exit(1)

    other_args = argv[:root_index] + argv[root_index+2:]

    parser = argparse.ArgumentParser(prog='searcher.py')
    subparser = parser.add_subparsers(dest='command', required=True)

    parser_init = subparser.add_parser('init')
    parser_init.add_argument('--drop-existing', action='store_true')

    subparser.add_parser('info')

    parser_add = subparser.add_parser('add')
    parser_add.add_argument('files', nargs='+')

    parser_find = subparser.add_parser('find')
    parser_find.add_argument('words', nargs='+')
    parser_find.add_argument('--limit', type=int, default=100)

    parsed = parser.parse_args(other_args)
    if parsed.command == 'init':
        init(root_dir, parsed.drop_existing)
    else:
        command_check(parsed, root_dir)


if __name__ == '__main__':
    main(sys.argv[1:])
