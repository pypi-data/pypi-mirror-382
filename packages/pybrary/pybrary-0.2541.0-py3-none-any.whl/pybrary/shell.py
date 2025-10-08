from functools import partial
import shlex
from subprocess import (
    CalledProcessError,
    PIPE,
    Popen,
    run,
)

from pybrary.ascii import rm_ansi_codes


def shell(script, shell, color=False):
    try:
        proc = run(
            script,
            stdout = PIPE,
            stderr = PIPE,
            check  = True,
            shell  = True,
            executable = shell,
        )
    except CalledProcessError as exc:
        ret = exc.returncode
        out = exc.stdout.decode('utf-8')
        err = exc.stderr.decode('utf-8')
    else:
        ret = proc.returncode
        out = proc.stdout.decode('utf-8').strip()
        err = proc.stderr.decode('utf-8').strip()

    if not color:
        out = rm_ansi_codes(out)
        err = rm_ansi_codes(err)

    return ret, out, err


def pipe(*cmds):
    prev = None
    for cmd in cmds:
        cmd = shlex.split(cmd)
        if prev:
            proc = Popen(cmd, stdin=prev.stdout, stdout=PIPE)
        else:
            proc = Popen(cmd, stdout=PIPE)
        prev = proc

    for line in proc.stdout.read().decode().strip().split('\n'):
        yield line.strip()


bash = partial(shell, shell='/bin/bash')


