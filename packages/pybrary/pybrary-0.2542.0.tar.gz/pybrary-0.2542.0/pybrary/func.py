from functools import wraps
from inspect import currentframe, getouterframes
from logging import getLogger
from operator import attrgetter
from pathlib import Path


# Full Qualified Name od obj
def fqn(obj):
    mod = getattr(obj, '__module__', None)
    cls = obj.__class__.__name__
    if 'builtin' in cls:
        mod = cls = None
    elif cls in ('type', 'function', 'method'):
        cls = None
    name = getattr(obj, '__name__', None)
    return '.'.join(n for n in (mod, cls, name) if n)


# caller's caller
def caller():
    frame = getouterframes(currentframe(), 2)[2]
    mod = Path(frame.filename).stem
    fct = frame.function
    return f'{mod}.{fct}'


# Default implementation for abstract methods
def todo(self):
    cls = self.__class__.__name__
    mth = getouterframes(currentframe())[1][3]
    raise NotImplementedError(
        f'\n ! {mth} missing in {cls} !\n'
    )


# Memoizing property decorator
def memo(fct):
    name = '_memo_' + fct.__name__
    get_val = attrgetter(name)
    @property
    def wrapper(self):
        try:
            return get_val(self)
        except AttributeError:
            val = fct(self)
            setattr(self, name, val)
            return val
    return wrapper


def singleton(cls):
    '''Singleton class decorator.

    Make cls a Singleton class.
    '''
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if wrapper.instance is None:
            wrapper.instance = cls(*args, **kwargs)
        return wrapper.instance
    wrapper.instance = None
    return wrapper


def cache(func):
    '''Cache decorator.

    Functools should be used instead.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key not in wrapper.cache:
            wrapper.cache[cache_key] = func(*args, **kwargs)
        return wrapper.cache[cache_key]
    wrapper.cache = {}
    return wrapper


def trace(func):
    '''Trace decorator.

    Log func calls and return values.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        debug = getLogger('trace').debug
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        debug(f"{func.__name__}({signature})")
        value = func(*args, **kwargs)
        debug(f"{func.__name__}() returned {repr(value)}")
        return value
    return wrapper
