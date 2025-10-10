from keyword import iskeyword
from pickle import dump, load

import nicely


class Dico(dict):
    def _cast(self, value):
        if (
            isinstance(value, dict)
            and not isinstance(value, Dico)
        ):
            if all(
                k.isidentifier() and not iskeyword(k)
                for k in value
            ):
                value = Dico(value)
        return value

    def __getitem__(self, item):
        try:
            value = super().__getitem__(item)
            return self._cast(value)
        except KeyError:
            value = self[item] = Dico()
            return value

    def __getattr__(self, attr):
        if attr.startswith('_'):
            value = super().__getattr__(attr)
            return value
        else:
            value = self[attr]
            return self._cast(value)

    def __setattr__(self, attr, val):
        if attr.startswith('_'):
            super().__setattr__(attr, val)
        else:
            self[attr] = self._cast(val)

    def __getstate__(self):
        return dict(self.items())

    def dump(self, path):
        items = dict(self)
        with open(path, 'wb') as out:
            dump(items, out)

    def load(self, path):
        with open(path, 'rb') as inp:
            items = load(inp)
        self.update(items)

    def __str__(self):
        return nicely.format(self)
