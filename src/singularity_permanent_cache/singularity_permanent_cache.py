#!/usr/bin/env python3

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

import argparse
import fcntl
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

DEFAULT_SINGULARITY_EXE = "singularity"


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Creates a permanent cache on disk for singularity "
                    "images. Returns the location of the image in the cache. "
                    "WARNING: This program will never check if a "
                    "newer image is available. Make sure unique tags or "
                    "hashes are used!")
    parser.add_argument("uri", metavar="<IMAGE>", type=str,
                        help="The singularity URI to the image. For example: "
                             "'docker://debian:buster-slim'")
    parser.add_argument("-d", "--cache-dir", required=False,
                        help="Path to the cache location. Uses the "
                             "SINGULARITY_PERMANENTCACHEDIR, "
                             "or SINGULARITY_CACHEDIR environment variable "
                             "by default.")
    parser.add_argument("-s", "--singularity-exe", type=str,
                        default=DEFAULT_SINGULARITY_EXE,
                        help="Path to singularity executable.")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase log verbosity. Can be used multiple "
                             "times.")
    parser.add_argument("-q", "--quiet", action="count", default=0,
                        help="Decrease log verbosity. Can be used multiple "
                             "times."
                        )
    return parser


def get_cache_dir_from_env() -> Path:
    singularity_permanentcachedir = os.environ.get(
        "SINGULARITY_PERMANENTCACHEDIR")
    singularity_cachedir = os.environ.get("SINGULARITY_CACHEDIR")
    if singularity_permanentcachedir:
        return Path(singularity_permanentcachedir)
    if singularity_cachedir:
        return Path(singularity_cachedir, "permanent_cache")
    raise OSError("Cannot determine a permanent cache dir from the "
                  "environment. Please set 'SINGULARITY_PERMANENTCACHEDIR' or "
                  "'SINGULARITY_CACHEDIR.")


class SimpleUnixFileLock:
    """
    Simple UNIX filelock. Uses fnctl.flock for locking a file. Implementation
    of https://github.com/benediktschmitt/py-filelock. This implementation
    is simpler and does not have all the features. Huge thanks to
    @benediktschmitt & contributors for this filelock example which they made
    Public Domain.
    """
    def __init__(self, file: str):
        self._file = file
        self._fd = None
        # Open mode is a combination of RDWR CREATE and TRUNC. By using bitwise
        # or symbol (|).
        self.open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
        self.log = logging.getLogger()

    def __enter__(self):
        # Use os.open because it is much faster than python open.  It also only
        # returns a file descriptor. Which is all that we need for locking.
        self._fd = os.open(self._file, self.open_mode)
        self.log.info("Waiting for file lock on: {0}".format(self._file))
        fcntl.flock(self._fd, fcntl.LOCK_EX)  # Exclusive lock, blocking
        self.log.debug("Lock acquired: {0}".format(self._file))

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self._fd, fcntl.LOCK_UN)
        os.close(self._fd)
        self.log.debug("Lock released: {0}".format(self._file))


def singularity_command(
        singularity_exe, *args, **kwargs
                        ) -> subprocess.CompletedProcess:
    """
    Execute a singularity command. Fails if singularity command fails.
    :param singularity_exe: Path to singularity executable.
    :param args: additional args for singularity.
    :param kwargs: kwargs for subprocess.run
    :return: a completed process.
    """
    result = subprocess.run([singularity_exe] + list(args),
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            check=True,
                            **kwargs)
    return result


def uri_to_filename(uri: str) -> str:
    """
    Replace characters that are forbidden on filesystems with underscores.
    In URIs for singularity/docker images these are ':' and '/'.
    :param uri: the uri for which characters are replaced.
    :return: a valid filename.
    """
    return uri.replace("://", "_").replace("/", "_").replace(":", "_")


def pull_image_to_cache(uri: str, cache_location: Optional[Path] = None,
                        singularity_exe=DEFAULT_SINGULARITY_EXE) -> Path:
    """
    Pull image to the cache.
    :param uri: Valid singularity image uri.
    :param cache_location: Location to pull the image to. If not given tries
                           to get the location from the environment.
    :param singularity_exe: path to singularity, only necessary if singularity
                            is not in PATH.
    :return: path to the image location.
    """
    log = logging.getLogger()

    if cache_location is None:
        cache = get_cache_dir_from_env()
        log.info("Cache dir from environment: {0}".format(cache))
    else:
        cache = cache_location

    if not cache.exists():
        log.warning("Cache dir does not yet exist. "
                    "Creating cache dir: {0}".format(str(cache)))
        cache.mkdir(parents=True)

    image_path = Path(cache, uri_to_filename(uri)).with_suffix(".sif")
    lockfile_path = Path(cache, ".lock")

    if not image_path.exists():
        with SimpleUnixFileLock(str(lockfile_path)):
            log.info("Start pulling image {0} to location {1}"
                     "".format(uri, str(image_path)))
            singularity_command(singularity_exe, "pull", str(image_path), uri)
    else:
        log.info("Image exists already at: {0}".format(str(image_path)))
    return image_path


def main():
    args = argument_parser().parse_args()
    log_level = max(logging.WARNING + (args.quiet - args.verbose) * 10, 0)
    log = logging.getLogger()  # gets the root logger.
    logging.basicConfig()  # This adds the default handler to the root logger.
    log.setLevel(log_level)
    cache_dir = Path(args.cache_dir) if args.cache_dir is not None else None
    image_path = pull_image_to_cache(args.uri, cache_dir,
                                     args.singularity_exe)
    print(image_path, end="")


if __name__ == "__main__":  # pragma: no cover
    main()
