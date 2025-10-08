import re


def negates(fct):
    def deco(*a, **k): return not fct(*a, **k)
    return deco


class Rex:
    def __init__(self, pat, match=True, switch=None, **opts):
        flags = re.IGNORECASE
        if opts.get('case', False): flags -= re.IGNORECASE
        if '\n' in pat: flags += re.VERBOSE
        flags += re.UNICODE
        self.pat = re.compile(pat, flags)
        self.match = self._match if match else negates(self._match)
        self.isin = self._isin if match else negates(self._isin)
        if switch: self.switch = switch

    def _match(self, txt):
        return self.pat.match(txt) and True or False

    def _isin(self, txt):
        return self.pat.search(txt) and True or False

    def find(self, txt):
        m = self.pat.search(txt)
        if m:
            return m.group()

    def findall(self, txt):
        found = list()
        for groups in self.pat.findall(txt):
            if isinstance(groups, tuple):
                for i in groups:
                    found.append(i)
            else:
                found.append(groups)
        return found

    def split(self, txt):
        return [i for i in self.pat.split(txt) if i]

    def replace(self, repl, txt, count=0):
        return self.pat.sub(repl, txt, count)

    def switch(self, txt):
        # to be overwritten. called by subfct.
        return txt

    def _repl(self, match):
        return self.switch(match.group())

    def subfct(self, txt, count=0):
        return self.pat.sub(self._repl, txt, count)

    def __str__(self):
        return self.pat.pattern


class Patterns:
    def __init__(self, pattern=None, match=True, **opts):
        self.incl = []
        self.excl = []
        self.valid = False
        if pattern:
            self(pattern, match, **opts)

    def __bool__(self):
        return self.valid

    def __call__(self, pat, match=True, **opts):
        if match:
            self.incl.append(Rex(pat, match=True, **opts))
        else:
            self.excl.append(Rex(pat, match=True, **opts))
        self.valid = True

    def matchany(self, txt):
        if not self.valid: return True
        excl = any(p.match(txt) for p in self.excl) if self.excl else False
        if excl: return False
        return any(p.match(txt) for p in self.incl) if self.incl else True

    def matchall(self, txt):
        if not self.valid: return True
        excl = all(p.match(txt) for p in self.excl) if self.excl else False
        if excl: return False
        return all(p.match(txt) for p in self.incl) if self.incl else True

    def findany(self, txt):
        if not self.valid: return True
        excl = any(p.isin(txt) for p in self.excl) if self.excl else False
        if excl: return False
        return any(p.isin(txt) for p in self.incl) if self.incl else True

    def findall(self, txt):
        if not self.valid: return True
        excl = all(p.isin(txt) for p in self.excl) if self.excl else False
        if excl: return False
        return all(p.isin(txt) for p in self.incl) if self.incl else True

    def find(self, txt):
        if any(p.isin(txt) for p in self.excl): return False
        return all(p.isin(txt) for p in self.incl)

    def __str__(self):
        return '{} - {}'.format(', '.join(map(str, self.incl)), ', '.join(map(str, self.excl)))


class Parser:
    def __init__(self, spec):
        tokens = self.make(spec)
        self.scan = re.Scanner(tokens).scan

    def make(self, spec):
        def handle(name):
            if name:
                return lambda scanner, token: (name, token)
        tokens = [
            (pattern, handle(name))
            for name, pattern in spec
        ]
        return tokens

    def parse(self, text):
        tokens, _ = self.scan(text)
        return tokens
