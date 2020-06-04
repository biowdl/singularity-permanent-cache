==========
Changelog
==========

.. Newest changes should be on top.

.. This document is user facing. Please word the changes in such a way
.. that users understand how the changes affect the new version.

version 1.0.0-alpha
---------------------------
+ Implemented a simple unix filelock to prevent race conditions.
+ Integrated functionality to determine the cache from environment variables.
+ Created a ``singularity-permanent-cache`` package that wraps the
  ``singularity_permanent_cache.py`` script.
