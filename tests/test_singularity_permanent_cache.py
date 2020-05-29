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

import pytest

from singularity_permanent_cache import get_cache_dir_from_env, uri_to_filename

# CACHE DIR TESTS


def test_get_cache_dir_from_env_sing_cachedir_set(monkeypatch):
    singularity_cache_dir = Path("singularity_cache")
    monkeypatch.setenv("SINGULARITY_CACHEDIR", str(singularity_cache_dir))
    assert get_cache_dir_from_env() == Path(singularity_cache_dir,
                                            "permanent_cache")


def test_get_cache_dir_from_env_perm_cachedir_set(monkeypatch):
    perm_cache_dir = Path("permanent")
    monkeypatch.setenv("SINGULARITY_PERMANENTCACHEDIR", str(perm_cache_dir))
    assert get_cache_dir_from_env() == perm_cache_dir


def test_get_cache_dir_from_env_no_env(monkeypatch):
    monkeypatch.delenv("SINGULARITY_CACHEDIR", raising=False)
    monkeypatch.delenv("SINGULARITY_PERMANENTCACHEDIR", raising=False)
    with pytest.raises(OSError) as error:
        get_cache_dir_from_env()
    error.match("Cannot determine a permanent cache dir from the environment.")
    error.match("Please set 'SINGULARITY_PERMANENTCACHEDIR' or "
                "'SINGULARITY_CACHEDIR.")

# URI tests
URIS = [
    ("docker://quay.io/biocontainers/bedtools:2.23.0--hdbcaa40_3",
     "docker_quay.io_biocontainers_bedtools_2.23.0--hdbcaa40_3"),
    ("docker://quay.io/biocontainers/"
     "mulled-v2-002f51ea92721407ef440b921fb5940f424be842:"
     "43ec6124f9f4f875515f9548733b8b4e5fed9aa6-0",
     "docker_quay.io_biocontainers_mulled-v2-"
     "002f51ea92721407ef440b921fb5940f424be842_"
     "43ec6124f9f4f875515f9548733b8b4e5fed9aa6-0"),
    ("docker://debian@sha256:"
     "f05c05a218b7a4a5fe979045b1c8e2a9ec3524e5611ebfdd0ef5b8040f9008fa",
     "docker_debian@sha256_"
     "f05c05a218b7a4a5fe979045b1c8e2a9ec3524e5611ebfdd0ef5b8040f9008fa"
     )
]


@pytest.mark.parametrize(["uri", "result"], URIS)
def test_uri_to_filename(uri, result):
    assert uri_to_filename(uri) == result
