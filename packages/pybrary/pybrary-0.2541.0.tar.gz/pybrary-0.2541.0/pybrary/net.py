from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_address, IPv4Address
from json import loads
from random import shuffle
from urllib.request import urlopen

from .commandparams import Param, ValidationError
from . import debug, error


ip_adr_getters = [
    'api.ipify.org',
    'api.my-ip.io/ip',
    'ident.me',
]


def request(url, json=False, timeout=2):
    try:
        with urlopen(url, timeout=timeout) as resp:
            if resp.status == 200:
                txt = resp.read().decode().strip()
                if json:
                    try:
                        return True, loads(txt)
                    except Exception as x:
                        reason = f'{type(x)} {x}'
                else:
                    return True, txt
            else:
                reason = f'{resp.status} {resp.reason}'
    except Exception as x:
        reason = f'{type(x)} {x}'

    reason = f'{url} ! {reason}'
    return False, reason


def get_text(url):
    return request(f'https://{url}')


def get_ip_adr():
    with ThreadPoolExecutor(
        max_workers = len(ip_adr_getters)
    ) as ex:
        for ok, result in ex.map(
            get_text,
            ip_adr_getters,
        ):
            if ok:
                return True, result
    error('unabled to get ip adr')
    return False, 'ERROR'


class ParamIPv4(Param):
    name = 'IPv4 adr'

    def verify(self, value):
        try:
            adr = ip_address(value)
            if not isinstance(adr, IPv4Address):
                raise ValueError
            return adr
        except ValueError:
            raise ValidationError(f'{value} is not IPv4')

