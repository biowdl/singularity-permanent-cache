#!/usr/bin/env python3

import sys
import subprocess
import time
from singularity_permanent_cache import SimpleUnixFileLock
from filelock import UnixFileLock
import shlex

if __name__ == "__main__":
    lockfile, wait_time, writefile, message = sys.argv[1:]

    with UnixFileLock(lockfile):
        time.sleep(float(wait_time))
        subprocess.run(shlex.split(f"bash -c 'echo {message} >> {writefile}'"))
