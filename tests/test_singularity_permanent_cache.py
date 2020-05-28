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

from pathlib import Path

from singularity_permanent_cache import get_cache_dir_from_env


def test_get_cache_dir_from_env_home(monkeypatch):
    from singularity_permanent_cache import get_cache_dir_from_env
    monkeypatch.setenv("HOME", "bla")
    assert get_cache_dir_from_env() == Path("bla", ".singularity", "cache",
                                            "permanent_cache")


def test_get_cache_dir_from_env_sing_cachedir_set(monkeypatch):
    singularity_cache_dir = Path("singularity_cache")
    monkeypatch.setenv("SINGULARITY_CACHEDIR", str(singularity_cache_dir))
    assert get_cache_dir_from_env() == Path(singularity_cache_dir,
                                            "permanent_cache")


def test_get_cache_dir_from_env_perm_cachedir_set(monkeypatch):
    perm_cache_dir = Path("permanent")
    monkeypatch.setenv("SINGULARITY_PERMANENTCACHEDIR", str(perm_cache_dir))
    assert get_cache_dir_from_env() == perm_cache_dir
