#!/usr/bin/env python3

import logging
import shlex
import subprocess
import sys
import time

from singularity_permanent_cache import SimpleUnixFileLock

if __name__ == "__main__":
    lockfile, writefile = sys.argv[1:]

    with SimpleUnixFileLock(lockfile):
        # We wait 0.1 second to make sure current time is distinct if the lock
        # works.
        time.sleep(0.1)
        current_time = str(round(time.time(), 1))
        subprocess.run(
            shlex.split(f"bash -c 'echo {current_time} >> {writefile}'"))
