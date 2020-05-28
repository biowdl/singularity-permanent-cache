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

import time
import threading
from pathlib import Path
import random
import tempfile
import multiprocessing

from singularity_permanent_cache import SimpleUnixFileLock


def test_filelock():
    count = 20
    random_wait_times = [random.random() / 10 for _ in range(count)]
    fd, _ = tempfile.mkstemp()
    _, count_file = tempfile.mkstemp()
    filelock = multiprocessing.Lock()

    def add_number(number: int, wait_time: float):
        with filelock:
            with open(count_file, "a") as count_h:
                time.sleep(wait_time)
                count_h.write(str(number) + '\n')

    threads = []
    for i, wait_time in enumerate(random_wait_times):
        thread = multiprocessing.Process(target=add_number, args=(i, wait_time))
        thread.start()
        # Wait a small amount of time between starting each process
        # Even multiprocessing.Lock() does not work correctly otherwise.
        time.sleep(0.003)
        threads.append(thread)

    for thread in threads:
        thread.join()
    executed_order = [int(line) for line in Path(count_file).read_text().splitlines()]
    assert executed_order == list(range(count))