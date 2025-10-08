from functools import partial
from datetime import datetime
from io import SEEK_END
from operator import attrgetter
import os, os.path, stat
from os import scandir, getcwd
from os.path import splitext, splitdrive, isfile, abspath
from pathlib import Path
from re import compile, match


def walk(path=None, recur=99):
    path = Path(path).expanduser()
    with scandir(path or getcwd()) as ls:
        for entry in sorted(ls, key=attrgetter('path')):
            if entry.is_dir(follow_symlinks=False):
                if recur:
                    yield from walk(entry.path, recur-1)
            elif entry.is_file():
                yield Path(entry)


def find(path, name):
    search = compile(name).search
    for path in walk(path):
        if search(str(path)):
            yield path


def grep(path, rex):
    search = compile(rex).search
    for line in open(path):
        if found := search(line):
            if groups := found.groupdict():
                yield groups
            elif groups := found.groups():
                yield groups
            else:
                yield line.rstrip()


class FileStat:
    def __init__(self, path):
        self.path = path if isinstance(path, Path) else Path(path)
        self.stat = os.stat(str(self.path))

    @property
    def mtime(self):
        mtime = self.stat[stat.ST_MTIME]
        return datetime.fromtimestamp(mtime)

    @property
    def age(self):
        delta = datetime.now() - self.mtime
        return delta.days


def last_lines(path, nb_lines, max_line_len=99):
    offset = nb_lines * max_line_len
    with open(path, 'rb') as inp:
        try:
            inp.seek(-offset, SEEK_END)
        except OSError:
            inp.seek(0)
        raw = inp.read()
    lines = raw.decode().split('\n')
    last = lines[-nb_lines:]
    return last


def split(full):
    path, name = os.path.split(full)
    drive, path = splitdrive(path)
    name, ext = splitext(name)
    ext = ext[1:]
    return path, name, ext
