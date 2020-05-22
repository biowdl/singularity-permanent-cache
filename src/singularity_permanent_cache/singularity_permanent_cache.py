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
import logging
import os
import subprocess
from pathlib import Path


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Creates a permanent cache on disk for singularity "
                    "images. WARNING: This program will never check if a "
                    "newer image is available. Make sure unique tags or "
                    "hashes are used!")
    parser.add_argument("uri", metavar="IMAGE",
                        help="The singularity URI to the image. For example: "
                             "'docker://debian:buster-slim'")
    parser.add_argument("-d", "--cache-dir", required=False)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-q", "--quiet", action="count", default=0)
    return parser


def get_cache_dir_from_env() -> Path:
    singularity_permanentcachedir = os.environ.get(
        "SINGULARITY_PERMANENTCACHEDIR")
    singularity_cachedir = os.environ.get("SINGULARITY_CACHEDIR")
    user_home = os.path.expanduser("~")
    if singularity_permanentcachedir:
        return Path(singularity_permanentcachedir)
    if singularity_cachedir:
        return Path(singularity_cachedir, "permanent_cache")
    if user_home:
        return Path(user_home, ".singularity", "cache", "permanent_cache")
    raise OSError("Cannot determine a permanent cache dir from the "
                  "environment. Please set 'SINGULARITY_PERMANENTCACHEDIR'.")


def singularity_command(singularity_exe="singularity", *args, **kwargs
                        ) -> subprocess.CompletedProcess:
    result = subprocess.run([singularity_exe] + list(args),
                            stderr = subprocess.PIPE,
                            stdout= subprocess.PIPE,
                            check=True,
                            **kwargs)
    return result


def uri_to_filename(uri: str) -> str:
    return uri.replace("://", "_").replace("/", "_").replace(":", "_")


def main():
    args = argument_parser().parse_args()
    log_level = logging.WARNING + (args.verbose - args.quiet) * 10
    log = logging.getLogger()
    log.setLevel(log_level)

if __name__ == "__main__":
    main()
