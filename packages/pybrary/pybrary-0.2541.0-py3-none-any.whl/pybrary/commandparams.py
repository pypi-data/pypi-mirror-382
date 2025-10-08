from pathlib import Path

from pybrary.command import Param, ValidationError


class ParamInt(Param):
    '''Int
    '''
    def verify(self, value):
        try:
            return int(value)
        except Exception as x:
            raise ValidationError(f'{value}') from x


class ParamPath(Param):
    '''Path
    '''
    def __init__(self, *a, **k):
        self.create = k.pop('create', False)
        super().__init__(*a, **k)


class ParamFile(ParamPath):
    '''File
    '''
    def verify(self, value):
        try:
            path = Path(value)
        except Exception as x:
            raise ValidationError(f'{value}') from x
        if path.is_file():
            return path
        elif self.create:
            try:
                path.open('x')
            except Exception as x:
                raise ValidationError(f'{value}') from x
        else:
            raise ValidationError(f'"{self.name}" File not found : {value}')


class ParamDir(ParamPath):
    '''Dir
    '''
    def verify(self, value):
        try:
            path = Path(value)
        except Exception as x:
            raise ValidationError(f'\n{value}') from x
        if path.is_dir():
            return path
        elif self.create:
            try:
                path.mkdir(parents=True)
            except Exception as x:
                raise ValidationError(f'{value}') from x
        elif path.exists():
            raise ValidationError(f'"{self.name}" : {value} is not a dir')
        else:
            raise ValidationError(f'"{self.name}" dir not found : {value}')
