from logging import getLogger
from os import remove, getcwd
from os.path import isfile
from shutil import copy
from functools import partial
from collections import deque

from pybrary import Rex, Patterns
from pybrary.files import  walk, split


logger = getLogger('pybrary.refiles')
debug = logger.debug


class Matcher:
    def __init__(self, root=None,
        full=None, path=None, name=None, ext=None, cont=None,
        not_full=None, not_path=None, not_name=None, not_ext=None, not_cont=None,
    **opts):
        self.root = root
        self.full = Patterns(full, **opts)
        self.path = Patterns(path, **opts)
        self.name = Patterns(name, **opts)
        self.ext = Patterns(ext, **opts)
        self.cont = Patterns(cont, **opts)
        if not_full:
            for x in not_full.split(';'):
                self.full(x, match=False, **opts)
        if not_path:
            for x in not_path.split(';'):
                self.path(x, match=False, **opts)
        if not_name:
            for x in not_name.split(';'):
                self.name(x, match=False, **opts)
        if not_ext:
            for x in not_ext.split(';'):
                self.ext(x, match=False, **opts)
        if not_cont:
            for x in not_cont.split(';'):
                self.cont(x, match=False, **opts)

    def check_byline(self, full, pat):
        excls = [p.isin for p in pat.excl]
        incls = [p.isin for p in pat.incl]
        for line in open(full):
            if any(excl(line) for excl in excls): return False
            incls = [incl for incl in incls if not incl(line)]
        return not incls

    def match(self, full, byline=True):
        full = str(full)
        path, name, ext = split(full)
        if not self.ext.find(ext): return False
        if not self.name.find(name): return False
        if not self.path.find(path): return False
        if not self.full.find(full): return False
        if self.cont:
            try:
                if byline:
                    return self.check_byline(full, self.cont)
                else:
                    return self.cont.find(open(full).read())
            except Exception as x:
                debug('match : %s ! %s', full, x)
                return False
        return True

    def find(self, root=None, recur=True, rel=True):
        return find(root, matcher=self, byline=True, recur=recur, rel=rel)

    def count(self, root=None):
        return count(root, matcher=self)

    def grep(self, fil, before=0, after=0):
        return grep(fil, before=before, after=after, matcher=self)

    def greper(self, fil, before=0, after=0, color=7):
        return greper(fil, before, after, matcher=self, color=color)

    def replace(self, fil, src, dst, **opt):
        replace(fil, src, dst, matcher=self, **opt)

    def __str__(self):
        return '\n'.join(p for p in [
            '\tfull : %s' % self.full if self.full else '',
            '\tpath : %s' % self.path if self.path else '',
            '\tname : %s' % self.name if self.name else '',
            '\text : %s' % self.ext if self.ext else '',
            '\tcont : %s' % self.cont if self.cont else '',
        ] if p)


def find(root=None, matcher=None, byline=True, recur=True, rel=True, **opts):
    matcher = matcher or Matcher(root, **opts)
    match = partial(matcher.match, byline=byline)
    walker = walk if recur else partial(walk, recur=0)
    root = root or matcher.root or getcwd()
    len_root = len(str(root))+1
    for fil in walker(root):
        if match(fil):
            fil = str(fil)
            yield fil[len_root:] if rel else fil


def count(**opts):
    return len(list(find(**opts)))


def _grep1(lines, matcher):
    find = matcher.cont.find
    for i, line in enumerate(lines, start=1):
        if find(line):
            yield i, line


def _grep2a(lines, before, after, matcher):
    size = before*2 + 1 + after*2
    current = before*2
    current_range = list(range(current-before, current+after+1))
    find = matcher.cont.find
    dq = deque(maxlen=size)
    done = set()

    def check(line, plage=current_range):
        if find(line):
            for k in plage:
                idx, line = dq[k]
                if idx in done: continue
                yield idx, line
                done.add(idx)

    for i, src in enumerate(lines, start=1):
        dq.append((i, src))
        if len(dq) < size: continue

        # first lines
        if dq[0][0] < current:
            for n, (idx, line) in enumerate(dq):
                if idx > current: break
                plage = range(max(n-before, 0), min(n+after+1, len(dq)))
                yield from check(line, plage)

        # most lines
        idx, line = dq[current]
        yield from check(line)

    # last lines
    for n, (idx, line) in enumerate(dq):
        plage = range(max(n-before, 0), min(n+after+1, len(dq)))
        yield from check(line, plage)


def _grep2b(lines, before, after, matcher):
    check = matcher.cont.find
    found = [
        nb
        for nb, line in enumerate(lines)
        if check(line)
    ]
    next_one, last_one = 0, len(lines)-1
    for nb in found:
        first = max(nb-before, next_one)
        last = min(nb+after, last_one)
        for i in range(first, last+1):
            yield i+1, lines[i]
            next_one = i+1


def grep(fil, cont=None, before=0, after=0, matcher=None, **opts):
    matcher = matcher or Matcher(cont=cont, **opts)
    lines = open(fil).read().split('\n')
    if before or after:
        return _grep2b(lines, before, after+1, matcher)
    else:
        return _grep1(lines, matcher)


def replace(fil, src, dst, cont=None, matcher=None, count=0, dry=True, bak=True, **opts):
    if not matcher:
        cont = cont or src
        matcher = Matcher(cont=cont, **opts)
    findall = matcher.cont.findall
    src = Rex(src)
    if dry:
        for i, lig in enumerate(open(fil), start=1):
            if findall(lig):
                lig=lig.strip()
                print('\t%i\t'%i, lig)
                print('\t   ->\t', src.replace(dst, lig, count))
    else:
        bakfil = fil+'_BAK'
        copy(fil, bakfil)
        w = open(fil, 'w')
        for lig in open(bakfil):
            if findall(lig):
                w.write(src.replace(dst, lig, count))
            else:
                w.write(lig)
        w.close()
        if not bak: remove(bakfil)


def color(txt, col=7):
    if col>7:
        return txt
    col+=30
    esc = chr(27)
    return f'{esc}[1;{col}m{txt}{esc}[0m'


def greper(fil, before=0, after=0, matcher=None, **opts):
    assert isfile(fil), '%s is not a file'%fil
    col = opts.pop('color', 7)
    if not matcher:
        matcher = Matcher(**opts)
    rex = matcher.cont.incl[0]
    for nb, line in matcher.grep(fil, before, after):
        for grp in rex.findall(line):
            line = line.replace(grp, color(grp, col))
        yield f'\t{nb:3d}\t{line}'

