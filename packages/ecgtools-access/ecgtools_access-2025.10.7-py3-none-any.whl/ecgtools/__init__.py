#!/usr/bin/env python
# flake8: noqa
"""Top-level module for ecgtools ."""

from . import _version
from .builder import Builder, RootDirectory, glob_to_regex

__version__ = _version.get_versions()['version']
