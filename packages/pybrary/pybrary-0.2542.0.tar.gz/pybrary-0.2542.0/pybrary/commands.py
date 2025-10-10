import pybrary


def get_ip_adr():
    try:
        ok, adr = pybrary.get_ip_adr()
        if ok:
            return True, adr
        else:
            return False, f'Error ! {adr}'
    except Exception as x:
        return False, f'Exception ! {x}'


def bash(script):
    ret, out, err = pybrary.bash(script)
    ok = ret==0
    return ok, out if ok else f'\n > {out}\n ! {err}\n'


def ssh(host, cmd):
    ssh = pybrary.SSH()
    rem = ssh.hosts[host]
    ret, out, err = rem.run(cmd)
    return ret==0, out.strip()


def known_hosts():
    ssh = pybrary.SSH()
    ssh.hosts.known()
    return True, ''


def find(root='.', pattern=r'.+\.py$'):
    for path in pybrary.find(root, pattern):
        print(path)
    return True, ''


def grep(pattern, root='.', files=r'.+\.py$'):
    for path in pybrary.find(root, files):
        header, footer = True, False
        try:
            for line in pybrary.grep(path, pattern):
                if header:
                    print(path)
                    header = False
                    footer = True
                print(f'\t{line}')
        except Exception as x:
            if header:
                print(path)
                header = False
            print(f' ! {x}')
            footer = True
        if footer:
            print()
    return True, ''

