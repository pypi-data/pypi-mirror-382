import json
from weakref import WeakSet


class Attribute:
    default = None
    mandatory = False

    def __init__(self, default=None, mandatory=False):
        # attr values or desc values
        self.default = default or self.default
        self.mandatory = mandatory or self.mandatory

    def __set_name__(self, cls, name):
        self.name = f'{cls.__name__}.{name}'
        self.attr = f'_{name}_'

    def __get__(self, obj, cls):
        return self.get(obj)

    def __set__(self, obj, val):
        try:
            validated = self.validate(val)
        except ValueError:
            self.invalid(val)
        if validated:
            self.set(obj, validated)
        else:
            self.invalid(val)

    def set(self, obj, val):
        setattr(obj, self.attr, val)

    def get(self, obj):
        return getattr(obj, self.attr, self.default)

    def validate(self, val):
        return val

    def invalid(self, val, msg=None):
        msg = f' ; {msg}' if msg else ''
        raise ValueError(f'Invalid {self.name} {type(val).__name__}({val}){msg}.')

    def dump(self, val):
        return val


class Property(Attribute):
    def __set__(self, obj, val):
        raise ValueError(f'{self.name} is read only.')


def clear(cls):
    cls.instances = WeakSet()
    for sub in cls.class_tree():
        sub.instances = WeakSet()


class Meta(type):
    def __init__(cls, name, bases, ns):
        super().__init__(name, bases, ns)
        cls.instances = WeakSet()


class Model(metaclass=Meta):
    _sentinel_ = None

    def __new__(cls, *a, **k):
        instance = super().__new__(cls)
        cls.instances.add(instance)
        return instance

    def __init__(self, *args, **kw):
        self.set_attrs(*args, **kw)
        self.validate()

    @property
    def lineage(self):
        return list(reversed(self.__class__.mro()[:-2]))

    def get_attrs(self):
        '''Get Model's Attributes.
        '''
        for cls in list(reversed(self.__class__.mro()))[2:]:
            for attr, desc in cls.__dict__.items():
                if attr.startswith('_'): continue
                if isinstance(desc, Attribute) and not isinstance(desc, Property):
                    yield attr, desc

    def set_attrs(self, *args, **kw):
        '''Set Attributes values from args.
        '''
        idx = 0
        for attr, desc in self.get_attrs():
            val = kw.pop(attr, None)
            if not val:
                try:
                    val = args[idx]
                except IndexError:
                    if desc.mandatory:
                        raise ValueError(f'Attribute {desc.name} is mandatory.') from None
                    # optional arg, will use default value.
                    continue
                idx += 1
            setattr(self, attr, val)

        if len(args) > idx:
            args = [str(a) for a in args[idx:]]
            raise ValueError(f'Invalid positional arguments for {self.__class__.__name__} : {", ".join(args)}')

        if kw:
            kw = [f'{k}={v}' for k, v in kw.items()]
            raise ValueError(f'Invalid keyword arguments for {self.__class__.__name__} : {", ".join(kw)}')

    @property
    def attrs(self):
        attrs = {
            attr : getattr(self, attr)
            for attr, _ in self.get_attrs()
        }
        return attrs

    @property
    def dict(self):
        items = {
            name : getattr(attr, 'attrs', attr)
            for name, attr in self.attrs.items()
        }
        return items

    @classmethod
    def class_tree(cls):
        yield cls
        for sub in cls.__subclasses__():
            yield from sub.class_tree()

    @classmethod
    def clear(cls):
        clear(cls)

    def dump(self):
        if self._sentinel_ is self:
            return '_self_'
        self._sentinel_ = self
        MODEL = self.__class__.mro()[1]   # noqa: N806
        data = dict()
        for name, desc in self.get_attrs():
            if attr := getattr(self, name):
                if isinstance(attr, MODEL):
                    val = attr.dump()
                    if val == '_self_':
                        continue
                else:
                    val = desc.dump(attr)
                if val:
                    if isinstance(val, Model):
                        val = val.dump()
                    data[name] = val
        self._sentinel_ = None
        return data

    def json(self, path='model'):
        with open(f'{path}.json', 'w') as out:
            data = self.dump()
            json.dump(data, out, indent=4)
        return data

    def __repr__(self):
        if self._sentinel_ is self:
            return '_self_'
        self._sentinel_ = self
        attrs = [
            (k, repr(v))
            for k, v in self.attrs.items()
            if v and repr(v) != '_self_'
        ]
        attrs = [
            (k, r)
            for k, r in attrs
            if r and r != '_self_'
        ]
        attrs = ', '.join(f'{key}={val}' for key, val in attrs)
        self._sentinel_ = None
        return f'{self.__class__.__name__}({attrs})'

    def validate(self):
        '''Validate Model after initialization.

        To be overwritten if needed.
        '''

