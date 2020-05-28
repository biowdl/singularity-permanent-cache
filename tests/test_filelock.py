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

import subprocess
import tempfile
from pathlib import Path


def test_filelock():
    count = 5
    lockfile = tempfile.mktemp()
    _, execution_times_file = tempfile.mkstemp()
    Path(execution_times_file).write_text("")  # make sure the file exists

    # this script uses the implemented filelock. It waits one second
    # after acquiring the lock and then writes the current time (in seconds) to
    # a file.
    filelockscript = Path(__file__).parent / "lockscript.py"

    # Start all the processes in quick succession.
    processes = [subprocess.Popen([str(filelockscript), lockfile,
                                   execution_times_file])
                 for _ in range(count)]

    # Wait on all processes to finish.
    for process in processes:
        process.wait()

    # Get the epoch time (in seconds) from the file. If the lock does not work
    # We expect multiple processes to have executed at the same time.
    # We use a set comprehension to collapse times that are the same.
    execution_times = {float(line) for line in
                       Path(execution_times_file).read_text().splitlines()}
    assert len(execution_times) == count
