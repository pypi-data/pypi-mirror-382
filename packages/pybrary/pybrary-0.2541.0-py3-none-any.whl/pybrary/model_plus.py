import json
from operator import attrgetter
import pickle

from pybrary.model_base import Attribute, Model


def select(cls, **where):
    getters = [
        (attrgetter(k.replace('_', '.')), v)
        for k, v in where.items()
    ]
    found = list()
    for sub in cls.class_tree():
        for obj in sub.instances:
            for get, val in getters:
                try:
                    if get(obj) != val: break
                except AttributeError: break
            else:
                found.append(obj)
    return found


def backup(cls, path=None):
    path = path or '/tmp/model.pkl'
    models = {
        sub.__name__ : tuple(sub.instances)
        for sub in cls.class_tree()
    }
    with open(path, 'wb') as out:
        pickle.dump(models, out)


def restore(cls, path=None):
    path = path or '/tmp/model.pkl'
    with open(path, 'rb') as inp:
        models = pickle.load(inp)   # noqa: S301
    return models


def export(cls, path=None):
    path = f'{path or cls.__name__}.json'
    models = {
        sub.__name__ : [i.dump() for i in sub.instances]
        for sub in cls.class_tree()
        if sub.instances
    }
    with open(path, 'w') as out:
        json.dump(models, out, indent=4)
    return models


class ModelPlus(Model):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.validate_attrs()

    def validate_attrs(self):
        for _name, attr in self.attrs.items():
            if isinstance(attr, Model):
                attr.validate()

    @classmethod
    def select(cls, **where):
        return select(cls, **where)

    @classmethod
    def backup(cls, path=None):
        backup(cls, path)

    @classmethod
    def restore(cls, path=None):
        return restore(cls, path)

    @classmethod
    def export(cls, path=None):
        return export(cls, path)


class Link(Attribute):
    def __init__(self, relation_name=None):
        self.relation_name = relation_name or object
        self._relation_ = None

    @property
    def relation(self):
        if not self._relation_:
            name = self.relation_name
            # if isinstance(name, type) and issubclass(name, Model):
            if isinstance(name, type):
                self._relation_ = name
            elif isinstance(name, str):
                for cls in Model.class_tree():
                    if cls.__name__ == name:
                        self._relation_ = cls
                        break
                else:
                    raise ValueError(f'Relation not found: {name}')
            else:
                raise ValueError(f'Invalid relation type : {type(name).__name__}')
        return self._relation_


class One(Link):
    def __set__(self, obj, val):
        if isinstance(val, self.relation):
            relation = val
        elif isinstance(val, dict):
            relation = self.relation(**val)
        elif isinstance(val, str):
            relation = self.relation(val)
        else:
            self.invalid(val, f'should be a {self.relation.__name__}')
        self.set(obj, relation)
        if isinstance(relation, Model):
            setattr(relation, type(obj).__name__.lower(), obj)


class Many(Link):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.items = list()

    def __get__(self, obj, cls):
        self._obj_ = obj
        return self

    def __set__(self, obj, val):
        raise ValueError(f'{self.name} is a list and cannot be set.')

    def __iter__(self):
        yield from self.items

    def add(self, relation):
        if not isinstance(relation, self.relation):
            self.invalid(relation, f'should be a {self.relation.__name__}')
        self.items.append(relation)
        if isinstance(relation, Model):
            attr_name = self._obj_.attr_name if hasattr(self._obj_, 'attr_name') else type(self._obj_).__name__.lower()
            setattr(relation, attr_name, self._obj_)

    def __repr__(self):
        if self.items:
            return ', '.join(str(i) for i in self.items if i)
        return ''

    def dump(self, val):
        return self.items

