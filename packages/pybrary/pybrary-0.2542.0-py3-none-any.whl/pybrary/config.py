from os import environ
from pathlib import Path
from subprocess import call

from pybrary.compat.warnings import deprecated
from pybrary import Dico


def escape(value):
    if isinstance(value, str):
        return value.replace('\\', '\\\\')
    else:
        return value


def create_config_py(path, defaults):
    kv = [(k, f"'{v}'" if isinstance(v, str) else v) for k, v in defaults.items()]
    kv = ',\n    '.join(f'{k} = {escape(v)}' for k, v in kv)
    with open(path, 'w') as out:
        out.write(f'config = dict(\n    {kv}\n)\n')

def create_config_toml(path, defaults):
    from toml import dump
    content = dict(config = defaults)
    with open(path, 'w') as out:
        dump(content, out)

def create_config_yaml(path, defaults):
    from yaml import dump
    content = dict(config = defaults)
    with open(path, 'w') as out:
        dump(content, out, indent=4)

def create_config_json(path, defaults):
    from json import dump
    content = dict(config = defaults)
    with open(path, 'w') as out:
        dump(content, out, indent=4)

creators = dict(
    py = create_config_py,
    toml = create_config_toml,
    yaml = create_config_yaml,
    json = create_config_json,
)


def load_config_py(path):
    from pybrary.modules import load
    return load('config', path).config

def load_config_toml(path):
    from tomllib import loads
    return loads(path.read_text())['config']

def load_config_yaml(path):
    from yaml import load, SafeLoader
    return load(open(path), Loader=SafeLoader)['config']

def load_config_json(path):
    from json import load
    return load(open(path))['config']

loaders = dict(
    py = load_config_py,
    toml = load_config_toml,
    yaml = load_config_yaml,
    json = load_config_json,
)


class Config:
    def __init__(self, app, defaults=None, ext='py'):
        self.app = app
        defaults = defaults or dict()
        found = self.find() or self.create(defaults, ext)
        self.config = Dico(found)

    def get_env(self, name):
        # NOTE : all value in environ are str
        key = f'{self.app}_{name}'
        val =  environ.get(key)
        return val

    def get(self, name):
        return self.get_env(name) or self.config.get(name)

    def __getattr__(self, name):
        return self.get(name)

    def __getitem__(self, name):
        return self.get(name)

    def __iter__(self):
        prefix = f'{self.app}_'
        env = [key for key in environ if key.startswith(prefix)]
        cfg = list(self.config.keys())
        return iter(env + cfg)

    def __contains__(self, name):
        return self.get(name) is not None

    @property
    def root(self):
        path = self.get_env('config_path') or f'~/.config/{self.app}'
        path = Path(path).expanduser()
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        return path

    def find(self):
        for ext, loader in loaders.items():
            full = self.root / f'config.{ext}'
            if full.is_file():
                config = loader(full)
                self.path = full
                return config

    def create(self, defaults, ext):
        full = self.root / f'config.{ext}'
        creators[ext](full, defaults)
        loader = loaders[ext]
        config = loader(full)
        self.path = full
        return config

    def edit(self):
        editor = environ.get('EDITOR', 'vim')
        call([editor, self.path])


@deprecated('Use pybrary.Config instaed')
def get_app_config(app):
    path = Path(f'~/.config/{app}').expanduser()
    try:
        from pybrary.modules import load
        full = path / 'config.py'
        config = load('config', full)
        return full, config.config
    except: pass
    try:
        from tomllib import loads
        full = path / 'config.toml'
        config = loads(full.read_text())
        return full, config
    except: pass
    try:
        from yaml import load, SafeLoader
        full = path / 'config.yaml'
        config = load(full, loader=SafeLoader)
        return full, config
    except: pass
    try:
        from json import load
        full = path / 'config.json'
        config = load(full)
        return full, config
    except: pass
    return None, None
