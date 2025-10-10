from functools import wraps
from inspect import (
    _empty,
    currentframe,
    getargvalues,
    getouterframes,
    signature,
)
from opcode import opname
from os import getcwd
from re import compile
from sys import settrace, path
from time import perf_counter_ns


lib_paths = (
    '_bootstr',
    '<.*>',
    'site-packages/.*',
)

lib_func = (
    '<.*>',
)


class Tracer:
    def __init__(self,
        label         = 'tracing',
        full_path     = False,
        show_types    = False,
        check_types   = False,
        show_times    = False,
        show_stamp    = False,
        stdlib        = False,
        format_arg_names = None,
        format_arg_types = None,
        dest          = None,
        buffered      = True,
        echo          = True,
        quiet         = True,
        ignored_funcs = None,
        ignored_paths = None,
    ):
        self.label = label
        self.level = 0
        self.offbak = list()
        self.full_path = full_path
        self.traces = list()
        self.show_types = show_types
        self.check_types = check_types
        self.ignored_paths = set()
        self.ignored_funcs = set()
        self.truncated = list()
        self.show_times = show_times
        self.show_stamp = show_stamp
        self.dest = dest or getcwd()
        self.buffered = buffered
        self.echo = echo
        self.quiet = quiet
        self.stdlib = stdlib
        self.setup(ignored_paths, ignored_funcs)
        self.format_arg_names = dict(
        )
        if format_arg_names:
            self.format_arg_names.update(format_arg_names)
        self.format_arg_types = {
            'list': self.format_arg_list,
            'dict': self.format_arg_dict,
            'function': self.format_arg_function,
            'generator': self.format_arg_generator,
        }
        if format_arg_types:
            self.format_arg_types.update(format_arg_types)


    @property
    def output(self):
        return f'{self.dest}/{self.label}.trace'

    def create(self):
        try:
            with open(self.output, 'x'):
                self.log(f'>>> {self.label}', ts=False)
        except FileExistsError: pass

    def write(self, line):
        with open(self.output, 'a') as out:
            out.write(f'{line}\n')

    def log(self, msg, ts=True):
        ts = f'{self.timestamp()}@{self.label[:12]:<12}' if ts and self.show_stamp else ''
        tab = '    ' * self.level
        msg = f'{ts}{tab}{msg}'
        if self.buffered:
            self.traces.append(msg)
        else:
            self.write(msg)
        if self.echo:
            print(msg)

    def log_exc(self, exc, info=None):
        if not self.quiet:
            msg = f'! {type(exc).__name__} ! {exc}'
            if info:
                msg = f'! {info} {msg}'
            self.log(msg)

    def dump(self):
        self.create()
        with open(self.output, 'a') as out:
            out.write('\n'.join(self.traces))

    def truncate(self, path):
        if not self.full_path:
            for pref in self.truncated:
                if path.startswith(pref):
                    path = path[len(pref)+1:]
        if path.endswith('.py'):
            path = path[:-3]
        return path

    def ignore_path(self, path):
        return self.ignored_paths.add(compile(path).search)

    def ignored_path(self, path):
        return any(ignore(path) for ignore in self.ignored_paths)

    def ignore_func(self, func):
        return self.ignored_funcs.add(compile(func).search)

    def ignored_func(self, func):
        return any(ignore(func) for ignore in self.ignored_funcs)

    def truncate_path(self, prefix):
        self.truncated.append(prefix)

    def timestamp(self):
        return perf_counter_ns()

    def start_timer(self):
        if self.show_times:
            self.timers[self.level] = self.timestamp()

    def stop_timer(self):
        if self.show_times:
            self.timers[self.level] = self.timestamp() - self.timers[self.level]

    @property
    def elapsed(self):
        if self.show_times:
            elapsed = self.timers[self.level] // 1_000_000
            if elapsed < 10000:
                return f' [{elapsed} ms]' if elapsed > 0 else ''
            else:
                return f' [{elapsed // 1000} s]'
        else:
            return ''

    def setup(self, ignored_paths, ignored_funcs):
        std_paths = [p for p in path if 'python' in p]
        std_paths.extend(lib_paths)
        if not self.stdlib:
            for p in std_paths:
                self.ignore_path(p)
        if ignored_paths:
            for p in ignored_paths:
                self.ignore_path(p)
        if not self.full_path:
            self.truncated.extend(std_paths)
        for func in lib_func:
            self.ignore_func(func)
        if ignored_funcs:
            for f in ignored_funcs:
                self.ignore_func(f)
        self.ignore_func(r'Tracer\..*')
        self.ignore_path('tracer')
        self.truncate_path(getcwd())
        self._exc_ = False
        self.timers = dict()

    def format_arg_type(self, val):
        return self.format_arg_types.get(type(val).__name__, str)(val)

    def format_arg_return(self, val):
        s = '' if val is None else self.format_arg_type(val)
        if self.show_types:
            s = f':{type(val).__name__} = {s}'
        return s

    def format_arg_name(self, name, val):
        formatter = self.format_arg_names.get(name)
        if formatter: return formatter(val)

    def format_arg(self, k, v):
        try:
            f = self.format_arg_name(k, v)
            if f is None:
                f = self.format_arg_type(v)
        except Exception as x:
            self.log_exc(x, f'{k}: {type(v).__name__}')
            f = ' ! '
        return f

    def format_arg_dict(self, val):
        return ', '.join(f'{k}:{self.format_arg(k, v)}' for k, v in val.items())

    def format_arg_list(self, val):
        return ', '.join(self.format_arg(i, v) for i, v in enumerate(val))

    def format_arg_function(self, func):
        mname = func.__module__
        mname = f'{mname}.' if mname!= '__main__' else ''
        fname = func.__qualname__.replace('.<locals>', '')
        return mname + fname

    def format_arg_generator(self, gen):
        gname = gen.__qualname__.replace('.<locals>', '')
        return gname

    def format_args(self, args):
        if self.show_types:
            return [f'{a if isinstance(a, str) else str(a)}:{type(a).__name__}' for a in args]
        else:
            return [a if isinstance(a, str) else str(a) for a in args]

    def format_kws(self, args):
        items = list()
        for k, v in args.items():
            f = self.format_arg(k, v)
            if self.show_types:
                t = type(args[k]).__name__
                s = f'{k}:{t} = {f}'
            else:
                s = f'{k} = {f}'
            items.append(s)
        return items

    def trace(self, file, line, func, args):
        if isinstance(args, tuple):
            if isinstance(args[0], str):
                pfx = args[0]
                if pfx == '>>>':
                    val = self.format_arg_return(args[1])
                    args = f' -> {val}{self.elapsed}'
                elif pfx == '-->':
                    val = self.format_arg_return(args[1])
                    args = f' >> {val}{self.elapsed}'
                elif pfx == '!!!':
                    args = f'{file}.{func}:{line}\n! {args[1].__name__} ! {args[2]}'
                else:
                    self.log(f'???2 {args}')
            elif len(args)==2 and isinstance(args[0], tuple) and isinstance(args[1], dict):
                args, kws = args
                args = ', '.join(a for a in self.format_args(args)) if args else ''
                kws = ', '.join(a for a in self.format_kws(kws)) if kws else ''
                sep = ', ' if args and kws else ''
                args = '('+ args + sep + kws +')'
            else:
                self.log(f'???3 {args}')
        else:
            self.log(f'???4 {args}')
        self.log(f'{file}:{line} {func}{args}')

    def ann_err(self, name, expected, actual):
        if name == '_return_':
            msg = f'! "should return "{expected.__name__}" not "{actual.__name__}" !'
        else:
            msg = f'! arg "{name}" should be "{expected.__name__}" not "{actual.__name__}" !'
        self.log(msg)

    def get_func_args(self, frame):
        arginfo = getargvalues(frame)
        args = arginfo.locals[arginfo.varargs] if arginfo.varargs else tuple()
        kws = arginfo.locals[arginfo.keywords] if arginfo.keywords else dict()
        return args, kws

    def get_sig(self, frame):
        fct = frame.f_code.co_name
        if fct.endswith('comp>'): return
        slf = frame.f_locals.get('self')
        if slf:
            # method
            func = getattr(slf, fct)
        else:
            try:
                # global function
                func = frame.f_globals[fct]
            except KeyError:
                # inner function
                outer = getouterframes(frame)[1]
                func = outer.frame.f_locals[fct]
        try:
            sig = signature(func)
        except Exception as x:
            sig = None
        return sig

    def chk_arg_ann(self, name, arg, ann):
        if ann is _empty: return
        if ann is None and arg is None: return
        try:
            if not isinstance(arg, ann):
                self.ann_err(name, ann, type(arg))
        except TypeError:
            self.log(f'! unable to  check arg ! {arg}:{ann}')

    def check_sig(self, frame, args):
        if self.check_types:
            sig = self.get_sig(frame)
            if not sig or not sig.parameters: return
            if isinstance(args, tuple) and args[0] == '>>>':
                arg = args[1]
                ann = sig.return_annotation
                self.chk_arg_ann('_return_', arg, ann)
            elif isinstance(args, dict):
                for name, p in sig.parameters.items():
                    arg = args[name]
                    ann = p.annotation
                    if ann is _empty: continue
                    self.chk_arg_ann(name, arg, ann)

    def get_func_name(self, frame):
        fct = frame.f_code.co_name
        slf = frame.f_locals.get('self')
        try:
            repr(slf) # check handlability
        except Exception:
            slf = None
        if slf:
            try:
                func = getattr(slf, fct)
            except Exception:
                func = None
        else:
            func = frame.f_globals.get(fct)
        try:
            return func.__qualname__
        except Exception:
            return fct

    def get_codename(self, frame):
        codeval = frame.f_code.co_code[frame.f_lasti]
        if not isinstance(codeval, int):
            codeval = ord(codeval)
        codename = opname[codeval]
        return codename

    def get_trace(self, frame, arg, lvl=0):
        path = frame.f_code.co_filename
        if self.ignored_path(path): return False
        func = self.get_func_name(frame)
        if self.ignored_func(func): return False
        self.level += lvl
        self.check_sig(frame, arg)
        path = self.truncate(path)
        line = frame.f_lineno
        self.trace(path, line, func, arg)
        return path, line, func, arg

    def trace_exception(self, frame, typ, val, tbk):
        ret = self.get_trace(frame, ('!!!', typ, val))
        if ret:
            self._exc_ = True

    def trace_return(self, frame, val):
        self.stop_timer()
        if self._exc_:
            self.level-=1
            self._exc_ = False
            return

        retname = self.get_codename(frame)
        if retname in ('RETURN_VALUE', 'RETURN_CONST'):
            pfx = '>>>'
        elif retname in ('YIELD_VALUE', 'YIELD_CONST'):
            pfx = '-->'
        elif retname in ('RAISE_VARARGS', 'RERAISE') and val is None:
            # return from __init__
            return
        else:
            # self.log(f'???1 {retname} {val}')
            pfx = retname

        if self.get_trace(frame, (pfx, val)):
            self.level-=1

    def trace_call(self, frame, event, arg):
        codename = self.get_codename(frame)
        if codename == 'YIELD_VALUE':
            # don't trace "yield from" calls, trace inner generator only
            return
        args = self.get_func_args(frame)
        self.get_trace(frame, args, 1)
        self.start_timer()
        return self.trace_event

    def trace_event(self, frame, event, arg):
        if event == 'call':
            return self.trace_call

        if event == 'return':
            self.trace_return(frame, arg)

        if event == 'exception':
            self.trace_exception(frame, *arg)

    def __enter__(self):
        if not self.buffered: self.create()
        self.log(f'{self.label} >>>', ts=False)
        self.offbak.append(self.level)
        self.level += 1
        if self.level == 1:
            settrace(self.trace_event)

    def __exit__(self, typ, val, tbk):
        self.level = self.offbak.pop()
        if self.level == 0:
            settrace(None)
        self.log(f'{self.label} <<<', ts=False)
        if self.buffered: self.dump()
        return self.quiet


_tracer_ = Tracer(
    label = 'trace',
    quiet = False,
)

def set_tracer(tracer=None, **k):
    global _tracer_
    if isinstance(tracer, Tracer):
        _tracer_ = tracer
    else:
        _tracer_ = Tracer(**k)

def trace(fct):
    @wraps(fct)
    def wrapper(*a, **k):
        caller = getouterframes(currentframe())[1]
        with _tracer_:
            _tracer_.log(f'< {_tracer_.truncate(caller.filename)}:{caller.lineno} {caller.function} > {caller.code_context[0].strip()}')
            _tracer_.level -= 1
            try:
                result = fct(*a, **k)
            except Exception as x:
                _tracer_.level += 1
                _tracer_.log_exc(x)
                result = None
        return result
    return wrapper
