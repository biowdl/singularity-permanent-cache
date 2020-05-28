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

import random
import subprocess
import tempfile
import time
from pathlib import Path


def test_filelock():
    count = 20
    random_wait_times = [random.random() for _ in range(count)]
    tmpfile = tempfile.mktemp()
    _, count_file = tempfile.mkstemp()
    with open(count_file, "wt") as count_h:
        count_h.write("")

    filelockscript = Path(__file__).parent / "lockscript.py"

    processes = []
    for i, wait_time in enumerate(random_wait_times):
        processes.append(subprocess.Popen([str(filelockscript), tmpfile, str(wait_time), count_file, str(i)]))
        time.sleep(0.1)

    for process in processes:
        process.wait()
    executed_order = [int(line) for line in Path(count_file).read_text().splitlines()]
    assert executed_order == list(range(count))