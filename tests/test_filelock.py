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
import random
import tempfile

from singularity_permanent_cache import SimpleUnixFileLock


def test_filelock():
    count = 20
    order = []
    random_wait_times = [random.random() / 10 for i in range(count)]
    fd, _ = tempfile.mkstemp()
    filelock = SimpleUnixFileLock(fd)

    def add_number(number: int, wait_time: float):
        with filelock:
            time.sleep(wait_time)
            order.append(number)

    threads = []
    for i, wait_time in enumerate(random_wait_times):
        thread = threading.Thread(target=add_number, args=(i, wait_time))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    assert order == list(range(count))