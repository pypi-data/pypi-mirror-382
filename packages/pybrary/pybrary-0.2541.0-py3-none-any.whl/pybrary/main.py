#!/home/louis/venv/pybrary/bin/python


def main(*args):
    print(f"\nmain({', '.join(args)})\n")


if __name__ == '__main__':
    from sys import argv
    main(*argv[1:])
