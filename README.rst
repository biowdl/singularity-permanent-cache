===========================
singularity-permanent-cache
===========================

.. Badges have empty alts. So nothing shows up if they do not work.
.. This fixes readthedocs issues with badges.
.. image:: https://img.shields.io/pypi/v/singularity-permanent-cache.svg
  :target: https://pypi.org/project/singularity-permanent-cache/
  :alt:

.. image:: https://img.shields.io/conda/v/conda-forge/singularity-permanent-cache.svg
  :target: https://anaconda.org/conda-forge/singularity-permanent-cache
  :alt:

.. image:: https://img.shields.io/pypi/pyversions/singularity-permanent-cache.svg
  :target: https://pypi.org/project/singularity-permanent-cache/
  :alt:

.. image:: https://img.shields.io/pypi/l/singularity-permanent-cache.svg
  :target: https://github.com/biowdl/singularity-permanent-cache/blob/master/LICENSE
  :alt:

.. image:: https://travis-ci.com/biowdl/singularity-permanent-cache.svg?branch=develop
  :target: https://travis-ci.com/biowdl/singularity-permanent-cache
  :alt:

.. image:: https://codecov.io/gh/biowdl/singularity-permanent-cache/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/biowdl/singularity-permanent-cache
  :alt:

Singularity-permanent-cache creates a permanent cache for singularity images on
disk. It takes a URI as argument and returns the location of the image. It
utilizes a filelock to prevent cache corruption.

It will use the
``SINGULARITY_PERMANENTCACHEDIR`` or ``SINGULARITY_CACHEDIR`` environment
variables to determine the location of the cache. Alternatively the cache dir
can be set with the ``-d`` or ``--cache-dir`` flags on the command line.

The ``singularity-permanent-cache`` command can be used in scripts. It was
designed with multiprocess usage in mind: a filelock will prevent corruption
of the cache when multiple instances of singularity-permanent-cache are
running. It can be used in a script like this:

.. code-block:: bash

    #!/usr/bin/env bash
    set -eu -o pipefail

    export SINGULARITY_PERMANENTCACHEDIR=$HOME/.singularity/permanent_cache
    MY_IMAGE_URI="docker://debian:buster-slim"
    IMAGE_LOCATION=$(singularity-permanent-cache $MY_IMAGE_URI)

    cluster_submit "singularity exec $IMAGE_LOCATION echo 'Hello world!'"

Singularity-permanent-cache will download the debian buster slim image
if it is not yet in the cache. It will not dowload anything if it is already
in the cache.

.. warning::

    Do not use ``singularity-permanent-cache`` on images with unstable tags
    such as ``docker://ubuntu:latest``. Once the ``docker_ubuntu_latest.sif``
    image is in the cache, ``singularity-permanent-cache`` will never check
    for a newer version!

    Use containers with stable tags, such as `biocontainers
    <https://biocontainers.pro>`_ or use hashes. (For example:
    ``ubuntu@sha256:a69390df0911533dd2fc552a8765481bf6a93b5d5952a9ddbe9cb64ca3479e17``.)

.. note::

    singularity-permanent-cache utilizes a filelock which only works if
    multiple singularity-permanent-cache processes are launched on the same
    machine. If multiple processes are launched on multiple machines connected
    to the same networked filesystem then cache corruption may occur.

Usage
----------------
Beside ``singularity-permanent-cache``, also ``spc`` is added to PATH as a
short-hand when installing the package. ``singularity-permanent-cache`` is
also available as a stand-alone script `singularity_permanent_cache.py
<https://github.com/biowdl/singularity-permanent-cache/releases>`_.

``singularity-permant-cache`` has no dependencies and only requires a modern
python version (3.5 or higher).

.. code-block::

    usage: singularity-permanent-cache [-h] [-d CACHE_DIR] [-s SINGULARITY_EXE]
                                   [--which-cache] [-v] [-q]
                                   <IMAGE>

    Creates a permanent cache on disk for singularity images. Returns the location
    of the image in the cache. WARNING: This program will never check if a newer
    image is available. Make sure unique tags or hashes are used!

    positional arguments:
      <IMAGE>               The singularity URI to the image. For example:
                            'docker://debian:buster-slim'

    optional arguments:
      -h, --help            show this help message and exit
      -d CACHE_DIR, --cache-dir CACHE_DIR
                            Path to the cache location. Uses the
                            SINGULARITY_PERMANENTCACHEDIR, or SINGULARITY_CACHEDIR
                            environment variable by default.
      -s SINGULARITY_EXE, --singularity-exe SINGULARITY_EXE
                            Path to singularity executable.
      --which-cache         Show which cache the program will use and exit.
      -v, --verbose         Increase log verbosity. Can be used multiple times.
      -q, --quiet           Decrease log verbosity. Can be used multiple times.


Acknowledgements
----------------
Lots of thanks to @TMiguelT, @illusional and @vsoch for their constructive
feedback on `this PR for Cromwell
<https://github.com/broadinstitute/cromwell/pull/5515>`_ which led to the
development of this program.

The filelock implementation is based on `py-filelock
<https://github.com/benediktschmitt/py-filelock>`_.
Huge thanks to @benediktschmitt & contributors for this filelock example
which they made Public Domain.
