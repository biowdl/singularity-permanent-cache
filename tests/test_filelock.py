# Copyright (c) 2020 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tempfile
import threading
import time
from pathlib import Path

from singularity_permanent_cache import SimpleUnixFileLock


def test_filelock():
    count = 5
    lockfile = tempfile.mktemp()
    _, execution_times_file = tempfile.mkstemp()
    Path(execution_times_file).write_text("")  # make sure the file exists

    def filelock_test():
        with SimpleUnixFileLock(lockfile):
            # We wait 0.1 second to make sure current time is distinct if the
            # lock works.
            time.sleep(0.1)
            current_time = str(round(time.time(), 1))
            # Use append mode here
            with open(execution_times_file, mode="at") as file_h:
                file_h.write(current_time + "\n")

    # Start all the processes in quick succession.
    threads = [threading.Thread(target=filelock_test) for _ in range(count)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Get the epoch time (in seconds) from the file. If the lock does not work
    # We expect multiple processes to have executed at the same time.
    # We use a set comprehension to collapse times that are the same.
    execution_times = {float(line) for line in
                       Path(execution_times_file).read_text().splitlines()}
    assert len(execution_times) == count
