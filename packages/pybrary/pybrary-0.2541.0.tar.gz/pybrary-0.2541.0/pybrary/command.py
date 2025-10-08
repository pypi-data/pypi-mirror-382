from os import environ
from sys import argv


class ValidationError(Exception):
    '''Validation Error'''


class SubCmdError(Exception):
    '''Sub Command Error'''


class Param:
    name = None
    positional = False
    mandatory = False
    default = None

    def __init__(self, parent):
        if not (self.__doc__ and self.__doc__.strip()):
            raise ValueError(
                f'"{self.__class__.__name__}" Param should have a doc string.'
            )
        if not self.name:
            raise ValueError(
                f'"{self.__class__.__name__}" Param should have a "name" attribute.'
            )
        self.parent = parent # command or param
        self.get = self.parent.get
        self.set = self.parent.set

    def verify(self, value):
        return value

    def validate(self, value):
        return self.verify(value)

    def check(self, val):
        try:
            v = self.validate(val)
        except ValidationError as x:
            v = f' ! {val} !'
        return v

    def help(self, command=None):
        if command:
            value = command.get(self.name)
            print(f'\n{self.name} = {value}')
        else:
            print(f'\n{self.name}')
        self.positional and print(' - Positional')
        self.mandatory and print(' - Mandatory')
        self.default and print(f' - Default : {self.default}')
        lines = [f'    {i}' for i in self.__doc__.strip().split('\n')]
        lines[0] = f'    * {lines[0].strip()} *'
        print('\n'.join(lines))


def mk_subparam(cmd):
    class SubCmdParam(Param):
        '''SubCmd
    Sub Command
        '''
        name = 'subcmd'
        positional = True
        mandatory = False
        command = cmd.__class__

        def verify(self, value):
            return self.command.subs.get(value)

    return SubCmdParam(cmd)


def parse_args(args=None):
    if args:
        opt = args.split()
    else:
        _cmd, *opt = argv

    args, kwds = [], {}
    for o in opt:
        if '=' in o:
            k, v = o.split('=')
            kwds[k] = v
        else:
            args.append(o)
    return args, kwds


class Command:
    config = None
    env_pfx = None
    subs = None
    vargs = False
    line = False
    Params = []
    shortcut = False

    def __init__(self, *Params, parent=None):
        if not (self.__doc__ and self.__doc__.strip()):
            raise ValueError(
                f'"{self.__class__.__name__}" Command should have a doc string.'
            )
        self.parent = parent
        self._args = list()
        self._kws = dict()
        self.params = dict()
        params = [P(self) for P in Params or self.Params]
        if self.subs:
            subparam = mk_subparam(self)
            params.append(subparam)
        self.specs = {
            p.name: p
            for p in params
        }
        self.positionals = [
            p
            for p in params
            if p.positional
        ]

    @property
    def args(self):
        return list(self._args)

    @property
    def kws(self):
        return {
            k:v
            for k,v in self._kws.items()
            if not k.startswith('_')
        }

    def get(self, name):
        if name in self.params:
            return self.params[name]
        if self.parent:
            return self.parent.get(name)

    def set(self, name, value):
        self.params[name] = value

    @property
    def env_prefix(self):
        def mk(pref):
            if isinstance(pref, str) and pref.strip():
                return f'{pref.strip()}_'
        pref = (
            mk(self.env_pfx)
            or mk(self.config and self.config.get('env_prefix'))
            or ''
        )
        return pref

    def validate(self, *a, **k):
        check = k.pop('_check', False)
        pick = k.pop('_pick', False)
        params = dict()

        if self.line:
            return dict(
                _line_ = ' '.join(a)
            )

        for i, p in enumerate(list(self.positionals)):
            if p.name in k:
                del self.positionals[i]

        if len(a) >  len(self.positionals):
            if not pick:
                raise ValidationError(f'Too many args : {len(a)}. Expected at most {len(self.positionals)}')

        for v, p in zip(a, self.positionals):
            try:
                val = p.check(v) if check else p.validate(v)
            except ValidationError:
                if self.config and p.name in self.config:
                    v = self.config[p.name]
                    val = p.check(v) if check else p.validate(v)
                else:
                    if p.default is None:
                        raise
                    else:
                        v = p.default
                        val = p.check(v) if check else p.validate(v)
            else:
                if pick and val:
                    self._args.remove(v)
            params[p.name] = val

        for name, val in k.items():
            if name in params:
                raise ValidationError(f'{name} is overridding positional arg')
            p = self.specs.get(name)
            if p:
                val = p.check(val) if check else p.validate(val)
                params[name] = val
                if pick:
                    del self._kws[name]
            else:
                if not pick:
                    params[name] = '?'
                    if not check:
                        raise ValidationError(f'Unsupported arg : {name}')

        for name, p in self.specs.items():
            if self.get(name):
                continue
            if name not in params and self.config:
                if name in self.config:
                    v  = self.config[name]
                    val = p.check(v) if check else p.validate(v)
                    params[name] = val
            if name not in params:
                var = f'{self.env_prefix}{name}'
                if var in environ:
                    v = environ[var]
                    val = p.check(v) if check else p.validate(v)
                    params[name] = val
            if name not in params and p.default:
                val = p.check(p.default) if check else p.validate(p.default)
                params[p.name] = val
            if name not in params:
                if p.mandatory:
                    params[name] = '!'
                    if not check:
                        raise ValidationError(f'Missing mandatory arg : {p.name}')
                else:
                    params[name] = None

        return params

    def get_params(self, args=None, _check=False, _pick=False):
        if args:
            a, k = parse_args(args)
        elif self.parent:
            a = self.parent.args
            k = self.parent._kws
        else:
            a, k = parse_args()

        if not _check:
            self._args = a
            self._kws = k

        k['_check'] = _check
        k['_pick'] = _pick

        try:
            # match and pick
            params = self.validate(*a, **k)
        except ValidationError:
            # no match
            raise
        else:
            # match, not pick
            if self._args == list(params.values()):
                self._args = []

        return params

    def __call__(self, args=None):
        if self.subs:
            try:
                self.params = self.get_params(args, _pick=True)
            except ValidationError:
                self.help()
                raise
            subcmd = self.params.get('subcmd')
            if subcmd:
                subcmd.parent = self
                try:
                    return subcmd()
                except ValidationError as x:
                    subcmd.help()
                    print(f'\n ! {x}\n')
                    raise SubCmdError
            else:
                for name, cmd in self.subs.items():
                    try:
                        if cmd.shortcut:
                            cmd.parent = self
                            try:
                                return cmd(args)
                            except SubCmdError:
                                return
                            except ValidationError:
                                continue
                        else:
                            cmd = cmd.subs and cmd.subs.get(self.args[0])
                            if cmd:
                                cmd.parent = self
                                self._args = self._args[1:]
                                a = self.args
                                k = ['='.join(i) for i in self.kws.items()]
                                return cmd(' '.join(a+k))
                    except Exception as x:
                        print(f' ! {name} - {cmd} ! {x} ! ')

            if self.parent:
                raise ValidationError
            else:
                self.help()

        else:
            try:
                params = self.get_params(args, _pick=self.vargs)
                self.params.update(params)
            except ValidationError as x:
                if self.parent and self.shortcut:
                    raise
                try:
                    self.help(args)
                except Exception as exc:
                    print(f' ! {exc}')
                    return
                print(f' ! {x}')
                return

            result = self.run()
            self.params = dict()
            return result


    def help(self, args=None, fetch=True):
        print(self.__doc__)
        if fetch:
            params = self.get_params(args, _check=True)
            for p in self.specs.values():
                p.help(self)
        else:
            for p in self.specs.values():
                p.help()
        print()
        if self.subs:
            subs = '\n    '.join(self.subs.keys())
            print(f'Sub Commands :\n    {subs}\n')
